from datetime import datetime, timedelta
from pypac import PACSession, get_pac
import sys
import re


class BaseScrape:
    def __init__(self,
        use_proxy:bool=False,
        proxy:str=None,
        pac_url:str=None
        ):
        """Class for scrapping webpages
        
        args:
        ----
        use_proxy - bool:False - should a proxy be used
        proxy - str:None - what is the address of the proxy ONLY VALID IF
            PROXY IS TRUE
        pac_Url - str:None - the location of the pac information ONLY VALID IF
            PROXY IS TRUE
        """
        self.pages_scraped = 0
        self.total_to_scrape = 0
        self.job_start = None
        self.job_end = None
        self.time_marks = []
        self.use_proxy = use_proxy
        self.proxy = proxy
        self.pac = get_pac(url=pac_url) if self.use_proxy else None
        self.pac_session = None

    def _deconstruct_url(self, url):
        if re.search(r"^http://", url):
            return "http", url[7:]
        elif re.search(r"^https://", url):
            return "https", url[8:]
        else:
            raise ValueError(f"Invalid url -> {url}")

    def _get_pac_session(self):
        if not self.pac_session:
            self.pac_session = PACSession(self.pac)
        return self.pac_session

    def _get_proxies(self, url):
        if self.use_proxy:
            #use pypac
            proxies = self.pac_session \
                ._get_proxy_resolver(self.pac) \
                .get_proxy_for_requests(url)
        else:
            proxies = None
        return proxies

    def _get_proxy(self, url):
        if self.use_proxy:
            if self.proxy:
                #use given proxy
                proxy = self.proxy
            elif self.pac:
                #use pypac
                proxies = self._get_proxies(url)
                match = re.search(r"^(\w*)", str(url))
                proxy = proxies[match.group()]
            else:
                raise ValueError("Either pac_url or a proxy must being given in order for use_proxy to be True")
        else:
            proxy = None
        return proxy

    def reset_pages_scraped(self):
        self.pages_scraped = 0
        self.time_marks = [datetime.now()]

    def increment_pages_scraped(self):
        self.pages_scraped += 1
        #Add time mark
        self.time_marks.append(datetime.now())
        #Calc loop time
        loop_time_elapsed = self.time_marks[-1] - self.time_marks[-2]
        #Calc estimated finish time
        total_time_elapsed = (datetime.now() - self.job_start).seconds
        est_total_time_s = total_time_elapsed + (self.total_to_scrape * total_time_elapsed / self.pages_scraped)
        #Output
        sys.stdout.write(f"\rprocessed -> {self.pages_scraped}/{self.total_to_scrape} - loop time {loop_time_elapsed} - est finish {datetime.now() + timedelta(seconds=est_total_time_s)}\n")
        sys.stdout.flush()

    def throttle_tasks(self):
        """Introduces sleep between tasks to slow them to a throttled rate"""
        pass

    def start_job(self):
        self.job_start = datetime.now()
        self.time_marks = [self.job_start]
        self.job_end = None

    def end_job(self):
        self.job_end = datetime.now()
        runtime = self.job_end - self.job_start
        print(f"Job completed in {runtime}")

    def _get_pac_session(self):
        if not self.pac_session:
            self.pac_session = PACSession(self.pac)
        return self.pac_session