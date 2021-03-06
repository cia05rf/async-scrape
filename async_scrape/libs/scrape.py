from time import sleep
import pandas as pd
from urllib3.exceptions import NewConnectionError
from requests_html import HTMLSession
import logging

from .base_scrape import BaseScrape


class Scrape(BaseScrape):
    def __init__(self,
        post_process_func:callable,
        post_process_kwargs:dict={},
        fetch_error_handler:callable=None,
        use_proxy:bool=False,
        proxy:str=None,
        pac_url:str=None,
        consecutive_error_limit:int=100,
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
        use_proxy - bool:False - should a proxy be used
        proxy - str:None - what is the address of the proxy ONLY VALID IF
            PROXY IS TRUE
        pac_Url - str:None - the location of the pac information ONLY VALID IF
            PROXY IS TRUE
        consecutive_error_limit - int:100 - the number of times an error can be experienced 
            in a row before the scrape is cancelled and a new round is started
        attempt_limit - int:5 - number of times a url can be attempted before it's abandoned
        rest_between_attempts - bool:True - should the program rest between scrapes
        rest_wait - int:60 - how long should the program rest for ONLY VALID IF
            REST_BETWEEN_SCRAPES IS TRUE
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
        self.session = HTMLSession()
        #Define allowed errors
        self.acceptable_errors = ()
        self.consecutive_error_limit = consecutive_error_limit
        self.consecutive_error_count = 0
        #Define criteria for looping multiple attempts
        self.attempt_limit = attempt_limit
        self.rest_between_attempts = rest_between_attempts
        self.rest_wait = rest_wait
        self.tracker_df = None
        self.cur_err = None

    def _proxy(self):
        #Start the pac session
        self._get_pac_session()
        self.session = self.pac_session
        
    def _fetch(self, url):
        """Function to fetch HTML from url
        
        args:
        ----
        url - str - url to be requested

        returns:
        ----
        list
        """
        resp = None
        #Make the request
        try:
            if url:
                resp = self.session.get(url, headers=self.headers)
                if resp.status_code == 200:
                    html = resp.text
                    func_resp = self.post_process(html=html, resp=resp, **self.post_process_kwargs)
                else:
                    func_resp = None
                #Reset self.acceptable_error_count if all goes fine
                self.consecutive_error_count = 0
                return {"url":url, "func_resp":func_resp, "status":resp.status_code, "error":None}
        except Exception as e:
            #Set the current error - increment if the same error
            if type(e) == self.cur_err:
                self.consecutive_error_count += 1
            else:
                self.cur_err = type(e)
                self.consecutive_error_count = 1
            #Check if acceptabe error limit has been reached
            # this prevents functions from carrying on after a site has started blocking calls
            if self.consecutive_error_count >= self.consecutive_error_limit:
                logging.warning(f"Consecutive error limit reached - {e} - consecutive count at {self.consecutive_error_count}/{self.consecutive_error_limit}")
            #Check for error handler
            if self.fetch_error_handler:
                logging.info(f"Error passed to {self.fetch_error_handler.__name__}")
                #Run the error handler
                self.fetch_error_handler(url, e)
            #Check if acceptable error
            if type(e) in self.acceptable_errors:
                logging.error(f"Acceptable error in request or post processing {url} - {e}")
            #Raise error
            else:
                logging.error(f"Unhandled error in request or post processing {url} - {e}")
                if f"{e}" == "":
                    raise e
            return {"url":url, "func_resp":None, "status":None, "error":e}

    def _increment_attempts(self, scraped:bool, urls:list=None):
        if urls:
            filter_df = self.tracker_df.url.isin(urls)
            self.tracker_df.loc[filter_df, "scraped"] = scraped
            self.tracker_df.loc[filter_df, "attempts"] += 1
        else:
            self.tracker_df["scraped"] = scraped
            self.tracker_df["attempts"] += 1

    #run from terminal
    def scrape_all(self, urls:list):
        """"Function scraping html from urls and passing 
        them through the post processing function
        
        args:
        ----
        urls - list - the pages to be scraped

        returns:
        ----
        list of dicts
            EG [{
                "url":"http://google.com",
                "success":True,
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
        while len(scrape_urls):
            self.reset_pages_scraped()
            self.total_to_scrape = len(scrape_urls)
            #Runt he scrapes
            scrape_resps = []
            for url in urls:
                scrape_resps.append(self._fetch(url))
                self.increment_pages_scraped()
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
            if len(scrape_urls) \
                and self.rest_between_attempts:
                logging.info(f"Sleeping for {self.rest_wait} seconds")
                sleep(self.rest_wait)
        logging.info(f"Scraping complete {len(failed_urls)} urls failed")
        #end the job
        self.end_job()
        return resps

    #run from terminal
    def scrape_one(self, url:str):
        """"Function scraping html from a single url and passing 
        it through the post processing function
        
        args:
        ----
        url - str - the pages to be scraped

        returns:
        ----
        list of dicts
            EG [{
                "url":"http://google.com",
                "success":True,
                "status":200
            }]
        """
        if self.use_proxy:
            self._proxy()
        for _ in range(self.attempt_limit):
            resp = self._fetch(url)
            if resp["status"]:
                break
            elif self.rest_between_attempts:
                logging.info(f"Sleeping for {self.rest_wait} seconds")
                sleep(self.rest_wait)
        return resp