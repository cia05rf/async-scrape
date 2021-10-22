import pytest
import traceback
import logging

from async_scrape import AsyncScrape
from async_scrape import Scrape

URLS = ["https://www.google.com"] * 100

def _post_process_func(html, resp):
    return None

def test_async_scrape_no_proxy():
    try:
        async_scrape = AsyncScrape(
            _post_process_func,
            use_proxy=False,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=60
        )
        resps = async_scrape.scrape_all(URLS)
        result = True if len(resps) == len(URLS) else False
    except Exception as e:
        result = False
    assert result is True

def test_scrape_all_no_proxy():
    try:
        scrape = Scrape(
            _post_process_func,
            use_proxy=False
        )
        resps = scrape.scrape_all(URLS)
        result = True if len(resps) == len(URLS) else False
    except Exception as e:
        logging.error(traceback.format_exc())
        result = False
    assert result is True

def test_scrape_one_no_proxy():
    try:
        scrape = Scrape(
            _post_process_func,
            use_proxy=True,
            attempt_limit=1
        )
        resps = scrape.scrape_one(URLS[0])
        result = True if resps["status"] else False
    except Exception as e:
        logging.error(traceback.format_exc())
        result = False
    assert result is True