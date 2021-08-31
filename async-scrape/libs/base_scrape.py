from datetime import datetime, timedelta
from pypac import PACSession, get_pac
import sys


class BaseScrape:
    def __init__(self,
        use_proxy:bool=False,
        proxy:str=None,
        pac_url:str=None
        ):
        """Class for scrapping webpages
        
        args:
        ----
        post_process_func - callable - for processing html
        post_process_kwargs - dict - kwargs for use in post processing
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