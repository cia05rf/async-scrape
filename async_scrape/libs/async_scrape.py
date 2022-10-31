
import asyncio
from datetime import datetime
from typing import List, Set, Union
import nest_asyncio
import aiohttp
import sys
import logging
import contextlib
from time import sleep

from aiohttp.client_exceptions import ServerDisconnectedError, ClientConnectionError
from asyncio.exceptions import TimeoutError
from urllib.error import URLError

from .base_scrape import BaseScrape
from ..utils.header_vars import random_header_vars
from ..utils.errors import HttpResponseStatusError


class AsyncScrape(BaseScrape):
    def __init__(self,
                 post_process_func: callable,
                 post_process_kwargs: dict = {},
                 fetch_error_handler: callable = None,
                 use_proxy: bool = False,
                 proxy: str = None,
                 pac_url: str = None,
                 consecutive_error_limit: int = 100,
                 attempt_limit: int = 5,
                 rest_between_attempts: bool = True,
                 rest_wait: int = 60,
                 call_rate_limit: int = None,
                 randomise_headers: bool = False
                 ):
        """Class for scrapping webpages

        args:
        ----
        post_process_func: callable
            for processing html
        post_process_kwargs: dict = {}
            kwargs for use in post processing
        fetch_error_handler: callable = None
            the function to be called if an
            error is experienced during _fetch. Passes in:
            url, error as arguments
        use_proxy: bool = False
            should a proxy be used
        proxy: str = None
            what is the address of the proxy ONLY VALID IF
            PROXY IS TRUE
        pac_url: str = None
            the location of the pac information ONLY VALID IF
            PROXY IS TRUE
        consecutive_error_limit: int = 100
            the number of times an error can be experienced 
            in a row before the scrape is cancelled and a new round is started
        attempt_limit: int = 5
            number of times a url can be attempted before it's abandoned
        rest_between_attempts: bool = True
            should the program rest between scrapes
        rest_wait: int = 60
            how long should the program rest for ONLY VALID IF
            REST_BETWEEN_SCRAPES IS TRUE
        call_rate_limit: int = None
            Should the rate of calls be limited. Fingure is calls per minute.
            WARNING - This is limited by running scrapes in batches. If this value
            is larger than the number of urls then no limiting will be applied.
        randomise_headers: bool = False
            should the headers be randomised after each request
        """
        # Init super
        super().__init__(
            use_proxy=use_proxy,
            proxy=proxy,
            pac_url=pac_url,
            call_rate_limit=call_rate_limit
        )
        self.post_process = post_process_func
        self.post_process_kwargs = post_process_kwargs
        self.randomise_headers = randomise_headers
        self.headers = random_header_vars(self.header_vars)
        self.fetch_error_handler = fetch_error_handler
        self.shutdown_initiated = False
        # Establish loop and coro
        self.loop = None
        self.coro = None
        self.gathered_tasks = None
        # Define allowed errors
        self.acceptable_errors = (ServerDisconnectedError, ClientConnectionError,
                                  TimeoutError, URLError, HttpResponseStatusError)
        self.consecutive_error_limit = consecutive_error_limit
        self.consecutive_error_count = 0
        # Define criteria for looping multiple attempts
        self.attempt_limit = attempt_limit
        self.rest_between_attempts = rest_between_attempts
        self.rest_wait = rest_wait
        self.tracker = None
        self.cur_err = None

    async def shutdown(self):
        # Mark shutdown as started
        self.shutdown_initiated = True
        logging.info("Shutdown of scrape initialized ...")
        self.gathered_tasks.cancel()

    def _proxy(self):
        # Set policy if using windows
        self._set_policy()
        # Start the pac session
        self._get_pac_session()

    def _set_policy(self):
        if sys.platform.startswith("win") \
                and sys.version_info[0] == 3 \
                and sys.version_info[1] >= 8:
            policy = asyncio.WindowsSelectorEventLoopPolicy()
            asyncio.set_event_loop_policy(policy)

    def _set_event_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = asyncio.get_event_loop()

    def _get_event_loop(self):
        self._set_event_loop()
        if isinstance(self.loop, asyncio.BaseEventLoop):
            nest_asyncio.apply()
        return self.loop

    async def _fetch(self,
                     session: aiohttp.ClientSession,
                     req_features: List[Union[str, dict]],
                     req_type: str = "GET"):
        """Function to fetch HTML from url

        args:
        ----
        session: aiohttp.ClientSession
        req_features: List[Union[str, dict]]
            the features of the request. 
            GET - this is a list with one entry [url] 
            POST - this is a list with two entries [url, payload] 
        req_type: str = "GET"
            The type of request to execute

        returns:
        ----
        list
        """
        # Regenerate headers
        if self.randomise_headers:
            self.headers = random_header_vars(self.header_vars)
        # Get the proxy for this url
        url, payload = req_features
        proxy = self._get_proxy(url)
        status = None
        # Fetch with aiohttp session
        try:
            async with session.request(
                req_type.lower(),
                url,
                json=dict(payload) if payload is not None else None,
                proxy=proxy,
                headers=self.headers
            ) as resp:
                status = resp.status
                if status == 200:
                    html = await resp.text()
                    func_resp = self.post_process(
                        html=html, resp=resp, **self.post_process_kwargs)
                else:
                    raise HttpResponseStatusError(
                        f"url responded with a http status of {status}")
                # Reset self.acceptable_error_count if all goes fine
                self.consecutive_error_count = 0
                return {"url": url, "req": req_features, "func_resp": func_resp, "status": resp.status, "error": None}
        except Exception as e:
            # Set the current error - increment if the same error
            if type(e) == self.cur_err:
                self.consecutive_error_count += 1
            else:
                self.cur_err = type(e)
                self.consecutive_error_count = 1
            # Check if acceptabe error limit has been reached
            # this prevents functions from carrying on after a site has started blocking calls
            if self.consecutive_error_count >= self.consecutive_error_limit \
                    and not self.shutdown_initiated:
                await self.shutdown()
                logging.warning(
                    f"Consecutive error limit reached - {e} - consecutive count at {self.consecutive_error_count}/{self.consecutive_error_limit}")
            # Check for error handler
            if self.fetch_error_handler:
                logging.info(
                    f"Error passed to {self.fetch_error_handler.__name__}")
                # Run the error handler
                self.fetch_error_handler(url, e)
            # Check if acceptable error
            if type(e) in self.acceptable_errors:
                logging.warning(
                    f"Acceptable error in request or post processing {req_features} - {e}")
            # Raise error
            else:
                logging.error(
                    f"Unhandled error in request or post processing {req_features} - {e}")
                if f"{e}" == "":
                    raise e
            return {"url": url, "req": req_features, "func_resp": None, "status": status, "error": e}

    async def _fetch_async(self,
                           session: aiohttp.ClientSession,
                           req_features: List[Union[str, dict]],
                           req_type: str = "GET"
                           ):
        """Function for getting routes from one locationt to another by different 
        modes of transport.

        args:
        ----
        session
            aiohttp.ClientSession() object
        req_features: List[Union[str, dict]]
            the features of the request. 
            GET - this is a list with one entry [url] 
            POST - this is a list with two entries [url, payload] 
        req_type: str = "GET"
            The type of request to execute

        returns:
        ----
        float - time (hours)
        """
        # Establish return object
        rtrn = {
            "req": req_features[0],
            "func_resp": None,
            "status": None
        }
        # Fetch
        rtrn = await self._fetch(session, req_features, req_type)
        # Increment the pages scraped
        self.increment_pages_scraped()
        return rtrn

    async def _fetch_all_async(self,
                               reqs_features: List[List[Union[str, dict]]],
                               req_type: str = "GET"):
        """"Async function for finding the latitude and 
        longitude of a list of locations

        args:
        ----
        reqs_features: List[List[Union[str, dict]]]
            These are the features for all requests. for:
            GET - each is a list with one entry [url] 
            POST - each is a list with two entries [url, payload] 
        req_type: str = "GET"
            The type of request to execute

        returns:
        ----
        gathered asyncio tasks
        """
        tasks = []
        resps = []
        async with aiohttp.ClientSession() as session:
            for rf in reqs_features:
                tasks.append(
                    self._fetch_async(
                        session,
                        rf,
                        req_type
                    )
                )
            self.gathered_tasks = asyncio.gather(*tasks)
            with contextlib.suppress(asyncio.CancelledError):
                _ = await self.gathered_tasks
            # Get results individually to deal with premature cancellation
            resps = [
                r.result() for r in self.gathered_tasks._children
                if not r.cancelled()
            ]
        return resps

    # run from terminal
    def scrape_all(self, urls: List[str] = [], payloads: List[dict] = None, req_type: str = "GET") -> List[dict]:
        """"Function asynchronously scraping html from urls and passing 
        them through the post processing function

        args:
        ----
        urls: List[str] = []
            the pages to be scraped
        payloads: List[dict] = None
            the payloads for each page
        req_type: str = "GET"
            The type of request to execute

        returns:
        ----
        list of dicts
            EG [{
                "url":"http://google.com",
                "func_resp":response from post process function,
                "status":200
            }]
        """
        self.start_job()
        if self.use_proxy:
            self._proxy()
        # Establish urls
        if not len(urls):
            return []
        resps = dict()
        reqs_features = self._build_req_features(urls, payloads)
        all_failed_reqs = set()
        logging.info(f"{len(reqs_features)} unique urls from {len(urls)}")
        # Set a dataframe for tracking the url attempts
        self.tracker = {
            req: {"scraped": False, "attempts": 0}
            for req in reqs_features
        }
        # Start the loop
        self.loop = self._get_event_loop()
        while len(reqs_features):
            init_len = len(reqs_features)
            # Ensure shutdown flag is reset self.shutdown_initiated
            self.shutdown_initiated = False
            self.reset_pages_scraped()
            self.total_to_scrape = len(reqs_features)
            # Create batches for rate limiting
            reqs_features = list(reqs_features)
            batches = [set(reqs_features[i:i+self.call_rate_limit])
                       for i in range(0, self.total_to_scrape, self.call_rate_limit)] \
                if self.call_rate_limit is not None \
                else [set(reqs_features)]
            reqs_features = set(reqs_features)
            scrape_resps = []
            for i, batch_reqs in enumerate(batches):
                st_time = datetime.now()
                # Gather tasks and run
                self.coro = self._fetch_all_async(
                    batch_reqs, req_type=req_type)
                # Build try except clause for premature cancellation
                scrape_resps.extend(self.loop.run_until_complete(self.coro))
                # Pause if call rate too fast
                if i < len(batches) - 1:
                    self.limit_call_rate(len(batch_reqs), st_time)
            # Process responses
            reqs_features, new_resps, failed_reqs = \
                self.handle_responses(reqs_features, scrape_resps, init_len)
            resps |= new_resps
            all_failed_reqs |= failed_reqs
            # Sleep before running again
            # - shutdown must have been initiated
            # - there must still be urls to scrape
            # - the rest between attempt flag must be set to True
            if self.shutdown_initiated \
                    and len(reqs_features) \
                    and self.rest_between_attempts:
                logging.info(f"Sleeping for {self.rest_wait} seconds")
                sleep(self.rest_wait)
        logging.info(
            f"Scraping complete {len(all_failed_reqs)}/{len(resps)} reqs failed")
        # Convert resps back
        resps = [v for _, v in resps.items()]
        # end the job
        self.end_job()
        return resps
