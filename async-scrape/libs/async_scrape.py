
import asyncio
import re
import nest_asyncio
import aiohttp
from pypac import PACSession
import sys
import logging
from libs.base_scrape import BaseScrape
import contextlib
import pandas as pd
from time import sleep

from aiohttp.client_exceptions import ServerDisconnectedError, ClientConnectionError


class AsyncScrape(BaseScrape):
    def __init__(self,
        post_process_func:callable,
        post_process_kwargs:dict={},
        fetch_error_handler:callable=None,
        use_proxy:bool=False,
        proxy:str=None,
        pac_url:str=None,
        acceptable_error_limit:int=100,
        attempt_limit:int=5,
        rest_between_attempts:bool=True,
        rest_wait:int=60
        ):
        """Class for scrapping webpages
        
        args:
        ----
        post_process_func - callable - for processing html
        post_process_kwargs - dict:{} - kwargs for use in post processing
        fetch_error_handler - callable:None - the function to be called if an
            error is experienced during _fetch. Passes in:
            url, error as arguments
        proxy - bool:False - should a proxy be used
        pac_Url - str:None - the location of the pac information ONLY VALID IF
            PROXY IS TRUE
        """
        #Init super
        super().__init__(
            use_proxy=use_proxy,
            proxy=proxy,
            pac_url=pac_url
        )
        self.post_process = post_process_func
        self.post_process_kwargs = post_process_kwargs
        self.headers = {}
        self.fetch_error_handler = fetch_error_handler
        self.shutdown_initiated = False
        #Establish loop and coro
        self.loop = None
        self.coro = None
        self.gathered_tasks = None
        #Define allowed errors
        self.acceptable_errors = (ServerDisconnectedError, ClientConnectionError)
        self.acceptable_error_limit = acceptable_error_limit
        self.acceptable_error_count = 0
        #Define criteria for looping multiple attempts
        self.attempt_limit = attempt_limit
        self.rest_between_attempts = rest_between_attempts
        self.rest_wait = rest_wait
        self.tracker_df = None
    
    async def shutdown(self):
        #Mark shutdown as started
        self.shutdown_initiated = True
        logging.info("Shutdown of scrape initialized ...")
        self.gathered_tasks.cancel()

    def _proxy(self):
        #Set policy if using windows
        if sys.platform.startswith("win") \
            and sys.version_info[0] == 3 \
            and sys.version_info[1] >= 8:
            self._set_policy()
        #Start the pac session
        self._get_pac_session()

    def _get_pac_session(self):
        if not self.pac_session:
            self.pac_session = PACSession(self.pac)
        return self.pac_session

    def _set_policy(self):
        policy = asyncio.WindowsSelectorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)

    def _get_event_loop(self):
        self.loop = asyncio.get_event_loop()
        if isinstance(self.loop, asyncio.BaseEventLoop):
            nest_asyncio.apply()
        return self.loop
        
    async def _fetch(self, session, url):
        """Function to fetch HTML from url
        
        args:
        ----
        session - aiohttp.ClientSession() object
        url - str - url to be requested

        returns:
        ----
        list
        """
        local_args = locals()
        #Get the proxy for this url
        if self.use_proxy:
            if self.proxy:
                #use given proxy
                proxy = self.proxy
            elif self.pac:
                #use pypac
                proxies = self.pac_session \
                    ._get_proxy_resolver(self.pac) \
                    .get_proxy_for_requests(url)
                match = re.search("^(\w*)", str(url))
                proxy = proxies[match.group()]
            else:
                raise ValueError("Either pac_url or a proxy must being given in order for use_proxy to be True")
        else:
            proxy = None
        #Fetch with aiohttp session
        try:
            async with session.request("get", url, proxy=proxy, headers=self.headers) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    func_resp = self.post_process(html=html, resp=resp, **self.post_process_kwargs)
                else:
                    func_resp = None
                #Reset self.acceptable_error_count if all goes fine
                self.acceptable_error_count = 0
                return {"url":url, "func_resp":func_resp, "status":resp.status, "error":None}
        except Exception as e:
            #Check if acceptabe error limit has been reached
            # this prevents functions from carrying on after a site has started blocking calls
            if self.acceptable_error_count >= self.acceptable_error_limit \
                and not self.shutdown_initiated:
                self.shutdown()
            if type(e) in self.acceptable_errors:
                self.acceptable_error_count += 1
                logging.warning(f"Acceptable error - {e} - consecutive count at {self.acceptable_error_count}/{self.acceptable_error_limit}")
            elif self.fetch_error_handler:
                logging.info(f"Error passed to {self.fetch_error_handler.__name__}")
                #Run the error handler
                self.fetch_error_handler(url, e)
            else:
                logging.error(f"Unacceptable error in request or post processing {url} - {e}")
            return {"url":url, "func_resp":None, "status":None, "error":e}

    async def _fetch_async(self, 
        session, url
        ):
        """Function for getting routes from one locationt to another by different 
        modes of transport.

        args:
        ----
        session - aiohttp.ClientSession() object
        url - str - url to be requested

        returns:
        ----
        float - time (hours)
        """
        #Establish return object
        rtrn = {
            "url": url,
            "func_resp": None,
            "status": None
            }
        #Fetch
        rtrn = await self._fetch(session, url)
        #Increment the pages scraped
        self.increment_pages_scraped()
        return rtrn

    async def _fetch_all_async(self, urls):
        """"Async function for finding the latitude and 
        longitude of a list of locations
        
        args:
        ----
        urls - list - the pages to be scraped

        returns:
        ----
        gathered asyncio tasks
        """
        tasks = []
        async with aiohttp.ClientSession() as session:
            for url in urls:
                tasks.append(
                    self._fetch_async(
                        session,
                        url
                        )
                    )
            self.gathered_tasks = asyncio.gather(*tasks)
            with contextlib.suppress(asyncio.CancelledError):
                _ = await self.gathered_tasks
            #Get results individually to deal with premature cancellation
            resps = [
                r.result() for r in self.gathered_tasks._children
                if not r.cancelled()
                ]
            return resps

    def _increment_attempts(self, scraped:bool, urls:list=None):
        if urls:
            filter_df = self.tracker_df.url.isin(urls)
            self.tracker_df.loc[filter_df, "scraped"] = scraped
            self.tracker_df.loc[filter_df, "attempts"] += 1
        else:
            self.tracker_df["scraped"] = scraped
            self.tracker_df["attempts"] += 1

    #run from terminal
    def scrape_all(self, urls:list=[]):
        """"Function asynchronously scraping html from urls and passing 
        them through the post processing function
        
        args:
        ----
        urls - list - the pages to be scraped

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
        #Establish urls
        if not len(urls):
            return []
        #Set a dataframe for tracking the url attempts
        self.tracker_df = pd.DataFrame([
            {"url":u, "scraped":False, "attempts":0}
            for u in urls
        ])
        resps = []
        i = 0
        scrape_urls = urls
        #Start the loop
        self.loop = self._get_event_loop()
        while len(scrape_urls):
            #Ensure shutdown flag is reset self.shutdown_initiated
            self.shutdown_initiated = False
            self.reset_pages_scraped()
            self.total_to_scrape = len(scrape_urls)
            #Gaher tasks and run
            self.coro = self._fetch_all_async(scrape_urls)
            #Build try except clause for premature cancellation
            scrape_resps = self.loop.run_until_complete(self.coro)
            #Add scrape_resps to resps
            resps.extend(scrape_resps)
            #Get scraped urls
            scraped_urls = [
                r["url"] for r in resps
                if not r["error"]
                ]
            #Increment attempts count on each scraped url
            self._increment_attempts(True, scrape_urls)
            #Get errored urls
            errored_urls = [
                r["url"] for r in resps
                if r["error"]
                ]
            #Increment attempts count on each attempted but failed (IE had an error 
            # but not cancelled)
            self._increment_attempts(False, errored_urls)
            #Remove scraped urls from scrape_urls
            scrape_urls = [
                u for u in scrape_urls
                if u not in scraped_urls
            ]
            #Remove urls where too many attempts have been made
            failed_urls = self.tracker_df[
                self.tracker_df.attempts >= self.attempt_limit
            ].url.to_list()
            scrape_urls = [
                u for u in scrape_urls
                if u not in failed_urls
            ]
            logging.info(f"Scraping round {i} complete, in this round - {len(scraped_urls)} urls scrapped, {len(errored_urls)} urls errored, {len(errored_urls) - len(scrape_urls)} urls failed, {len(scrape_urls)} remain unscrapped")
            #Increment the loop number 
            i += 1
            #Sleep before running again
            # - shutdown must have been initiated
            # - there must still be urls to scrape
            # - the rest between attempt flag must be set to True 
            if self.shutdown_initiated \
                and len(scrape_urls) \
                and self.rest_between_attempts:
                logging.info(f"Sleeping for {self.rest_wait} seconds")
                sleep(self.rest_wait)
        logging.info(f"Scraping complete {len(failed_urls)} urls failed")
        #end the job
        self.end_job()
        return resps