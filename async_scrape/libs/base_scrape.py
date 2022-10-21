from datetime import datetime, timedelta
from typing import List
from pypac import PACSession, get_pac
import sys
import re
import logging
from time import sleep


class BaseScrape:
    def __init__(self,
                 use_proxy: bool = False,
                 proxy: str = None,
                 pac_url: str = None,
                 call_rate_limit: int = None
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
        self.pac = get_pac(url=pac_url) \
            if self.use_proxy and pac_url is not None else None
        self.pac_session = None
        # Variables for randomly generating headers
        self.header_vars = None
        self.call_rate_limit = call_rate_limit

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
            # use pypac
            proxies = self.pac_session \
                ._get_proxy_resolver(self.pac) \
                .get_proxy_for_requests(url)
        else:
            proxies = None
        return proxies

    def _get_proxy(self, url):
        if self.use_proxy:
            if self.proxy:
                # use given proxy
                proxy = self.proxy
            elif self.pac:
                # use pypac
                proxies = self._get_proxies(url)
                match = re.search(r"^(\w*)", str(url))
                proxy = proxies[match.group()]
            else:
                raise ValueError(
                    "Either pac_url or a proxy must being given in order for use_proxy to be True")
        else:
            proxy = None
        return proxy

    def rate_limit_pause(self, t: float) -> None:
        logging.info(f"Call rate limit exceeded, pausing for {t:.02f} seconds")
        sleep(t)

    def rate_limit_time(self, i: int, st_time: datetime) -> float:
        if self.call_rate_limit is not None:
            rate = (datetime.now() - st_time).total_seconds() \
                / (i+1)
            rate_limit = 60 / self.call_rate_limit
            if rate < rate_limit:
                return rate_limit - rate
            else:
                return 0
        else:
            return 0

    def handle_responses(self,
                         scrape_urls: List[str],
                         scrape_resps: dict,
                         init_len: int
                         ):
        # Add scrape_resps to resps
        new_resps = {r["url"]: r for r in scrape_resps}
        # Get scraped urls
        # Split success and fails
        success_urls = set([
            r["url"] for r in scrape_resps
            if not r["error"]
        ])
        errored_urls = set([
            r["url"] for r in scrape_resps
            if r["error"]
        ])
        # Increment attempts count on each scraped url
        self._increment_attempts(True, scrape_urls)
        # Increment attempts count on each attempted but failed (IE had an error
        # but not cancelled)
        self._increment_attempts(False, errored_urls)
        # Remove scraped urls from scrape_urls
        scrape_urls = scrape_urls.difference(success_urls)
        # Remove urls where too many attempts have been made
        failed_urls = set(k for k, v in self.tracker.items()
                          if v["attempts"] >= self.attempt_limit)
        scrape_urls = scrape_urls.difference(failed_urls)
        logging.info(f"""Scraping round complete, summary:
    attempted:                               {init_len}
    successful scrapes:                      {len(success_urls)}
    errored scrapes (will attempt again):    {len(errored_urls)}
    failed scrapes (will not attempt again): {len(failed_urls)}
    remaining urls:                          {len(scrape_urls)}""")
        return [scrape_urls, new_resps, failed_urls]

    def _increment_attempts(self, scraped: bool, urls: list = []):
        for u in urls:
            self.tracker[u]["scraped"] = scraped
            self.tracker[u]["attempts"] += 1

    def reset_pages_scraped(self):
        self.pages_scraped = 0
        self.time_marks = [datetime.now()]

    def increment_pages_scraped(self):
        self.pages_scraped += 1
        # Add time mark
        self.time_marks.append(datetime.now())
        # Calc estimated finish time
        total_time_elapsed = (datetime.now() - self.job_start).total_seconds()
        est_total_time_s = total_time_elapsed + \
            (self.total_to_scrape * total_time_elapsed / self.pages_scraped)
        # Calc av time
        avg_time_elapsed = total_time_elapsed / self.pages_scraped
        # Output
        sys.stdout.write(
            f"\rprocessed -> {self.pages_scraped}/{self.total_to_scrape} - avg time {avg_time_elapsed:.3f} - total time {timedelta(seconds=total_time_elapsed)} - est finish {datetime.now() + timedelta(seconds=est_total_time_s)}")
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
        logging.info(f"Job completed in {runtime}")

    def _get_pac_session(self):
        if not self.pac_session:
            self.pac_session = PACSession(self.pac)
        return self.pac_session
