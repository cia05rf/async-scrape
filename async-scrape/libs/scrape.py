from time import sleep
from urllib3.exceptions import NewConnectionError
from requests_html import HTMLSession
import logging

from scraping.libs.base_scrape import BaseScrape


class Scrape(BaseScrape):
    def __init__(self,
        post_process_func:callable,
        post_process_kwargs:dict={},
        proxy:bool=False,
        pac_url:str=None):
        """Class for scrapping webpages
        
        args:
        ----
        None
        """
        #Init super
        super().__init__(
            proxy=proxy,
            pac_url=pac_url
        )
        self.post_process = post_process_func
        self.post_process_kwargs = post_process_kwargs
        self.headers = {}
        self.session = HTMLSession()
        
    def _fetch(self, url):
        """Function to fetch HTML from url
        
        args:
        ----
        url - str - url to be requested

        returns:
        ----
        list
        """
        out = None
        resp = None
        try:
            if url:
                resp = self.session.get(url, headers=self.headers)
                if resp.status_code == 200:
                    html = resp.text
                    out = self.post_process(html=html, **self.post_process_kwargs)
        except NewConnectionError as e:
            #Pause and then retry
            sleep(60)
            return self._fetch(url)
        except Exception as e:
            logging.error(f"Error in request or post processing for {url} - {e}")
        finally:
            return {
                "url":url,
                "out":out,
                "status":resp.status_code if resp else None
            }

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
        if self.proxy:
            self.session = self._get_pac_session()
        self.total_to_scrape = len(urls)
        resps = []
        for url in urls:
            resps.append(self._fetch(url))
            self.increment_pages_scraped()
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
        if self.proxy:
            self.session = self._get_pac_session()
        resp = self._fetch(url)
        return resp