from datetime import datetime, timedelta
from typing import List, Set
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
        pac_url - str:None - the location of the pac information ONLY VALID IF
            PROXY IS TRUE
        """
        self.pages_scraped = 0
        self.total_to_scrape = 0
        self.job_start = None
        self.job_end = None
        self.time_marks = []
        self.use_proxy = use_proxy
        self.proxy = proxy
        self.pac = get_pac(req=pac_url) \
            if self.use_proxy and pac_url is not None else None
        self.pac_session = None
        # Variables for randomly generating headers
        self.header_vars = None
        self.call_rate_limit = call_rate_limit

    def _deconstruct_req(self, req):
        if re.search(r"^http://", req):
            return "http", req[7:]
        elif re.search(r"^https://", req):
            return "https", req[8:]
        else:
            raise ValueError(f"Invalid req -> {req}")

    def _get_pac_session(self):
        if not self.pac_session:
            self.pac_session = PACSession(self.pac)
        return self.pac_session

    def _get_proxies(self, req):
        if self.use_proxy:
            # use pypac
            proxies = self.pac_session \
                ._get_proxy_resolver(self.pac) \
                .get_proxy_for_requests(req)
        else:
            proxies = None
        return proxies

    def _get_proxy(self, req):
        if self.use_proxy:
            if self.proxy:
                # use given proxy
                proxy = self.proxy
            elif self.pac:
                # use pypac
                proxies = self._get_proxies(req)
                match = re.search(r"^(\w*)", str(req))
                proxy = proxies[match.group()]
            else:
                raise ValueError(
                    "Either pac_url or a proxy must being given in order for use_proxy to be True")
        else:
            proxy = None
        return proxy

    def _build_req_features(self, urls: List[str], payloads: List[dict] = None) -> Set[str]:
        """Build request batches for post requests"""
        # Convert payloads to hashable types (tuple)
        if payloads is None:
            payloads = [None for _ in range(len(urls))]
        else:
            payloads = [
                tuple(v.items())
                if isinstance(v, dict) else None
                for v in payloads
            ]
        # Adjust length of payload
        if len(payloads) < len(urls):
            payloads += [None for _ in range(len(urls) - len(payloads))]
        elif len(payloads) > len(urls):
            payloads = payloads[:len(urls)]
        # Zip
        reqs_features = set(zip(urls, payloads))
        return reqs_features

    def limit_call_rate(self, call_count: int, st_time: datetime) -> float:
        if self.call_rate_limit is not None:
            rate = (datetime.now() - st_time).total_seconds() \
                / call_count
            rate_limit = 60 / self.call_rate_limit
            if rate < rate_limit:
                t = (rate_limit - rate) * call_count
                sys.stdout.write(
                    f"\nCall rate limit exceeded ({rate:.2f}<{rate_limit:.2f}), pausing for {t:.02f} seconds")
                sleep(t)

    def handle_responses(self,
                         reqs_features: Set[tuple],
                         scrape_resps: dict,
                         init_len: int
                         ):
        # Add scrape_resps to resps
        new_resps = {r["req"]: r for r in scrape_resps}
        # Get scraped reqs
        # Split success and fails
        success_reqs = set([
            r["req"] for r in scrape_resps
            if not r["error"]
        ])
        errored_reqs = set([
            r["req"] for r in scrape_resps
            if r["error"]
        ])
        # Increment attempts count on each scraped req
        self._increment_attempts(True, reqs_features)
        # Increment attempts count on each attempted but failed (IE had an error
        # but not cancelled)
        self._increment_attempts(False, errored_reqs)
        # Remove scraped reqs from reqs_features
        reqs_features = reqs_features.difference(success_reqs)
        # Remove reqs where too many attempts have been made
        failed_reqs = set(k for k, v in self.tracker.items()
                          if v["attempts"] >= self.attempt_limit)
        reqs_features = reqs_features.difference(failed_reqs)
        logging.info(f"""Scraping round complete, summary:
    attempted:                               {init_len}
    successful scrapes:                      {len(success_reqs)}
    errored scrapes (will attempt again):    {len(errored_reqs)}
    failed scrapes (will not attempt again): {len(failed_reqs)}
    remaining reqs:                          {len(reqs_features)}""")
        return [reqs_features, new_resps, failed_reqs]

    def _increment_attempts(self, scraped: bool, reqs: list = []):
        for u in reqs:
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
            f"\rprocessed -> {self.pages_scraped}/{self.total_to_scrape} - avg time {avg_time_elapsed:.3f} - total time {timedelta(seconds=total_time_elapsed)} - est finish {(datetime.now() + timedelta(seconds=est_total_time_s)).strftime('%Y-%m-%d %H:%M:%S')}")
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
