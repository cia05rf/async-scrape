import pytest
import traceback
import logging

from async_scrape import AsyncScrape
from async_scrape import Scrape

# Hardcoded urls for testing
URLS = ['https://www.google.com/search?q=weather',
        'https://www.google.com/search?q=facebook',
        'https://www.google.com/search?q=youtube',
        'https://www.google.com/search?q=amazon',
        'https://www.google.com/search?q=nba',
        'https://www.google.com/search?q=pornhub',
        'https://www.google.com/search?q=nfl',
        'https://www.google.com/search?q=gmail',
        'https://www.google.com/search?q=google+translate',
        'https://www.google.com/search?q=xnxx',
        'https://www.google.com/search?q=xvideos',
        'https://www.google.com/search?q=google+maps',
        'https://www.google.com/search?q=yahoo+mail',
        'https://www.google.com/search?q=google',
        'https://www.google.com/search?q=home+depot',
        'https://www.google.com/search?q=food+near+me',
        'https://www.google.com/search?q=ebay',
        'https://www.google.com/search?q=translate',
        'https://www.google.com/search?q=usps+tracking',
        'https://www.google.com/search?q=yahoo']


def _post_process_func(html, resp):
    return "Hello world"


def test_async_scrape_no_proxy():
    try:
        async_scrape = AsyncScrape(
            _post_process_func,
            use_proxy=False,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=60,
            call_rate_limit=None,
            randomise_headers=True
        )
        resps = async_scrape.scrape_all(URLS)
        urls = set(URLS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(urls) else False
    except Exception as e:
        result = False
    assert result is True


def test_async_scrape_no_proxy_call_rate_limited():
    try:
        async_scrape = AsyncScrape(
            _post_process_func,
            use_proxy=False,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=60,
            call_rate_limit=10,
            randomise_headers=True
        )
        resps = async_scrape.scrape_all(URLS)
        urls = set(URLS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(urls) else False
    except Exception as e:
        result = False
    assert result is True


def test_scrape_all_no_proxy():
    try:
        scrape = Scrape(
            _post_process_func,
            use_proxy=False,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=60,
            call_rate_limit=None,
            randomise_headers=True
        )
        resps = scrape.scrape_all(URLS)
        urls = set(URLS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(urls) else False
    except Exception as e:
        logging.error(traceback.format_exc())
        result = False
    assert result is True


def test_scrape_all_no_proxy_call_rate_limited():
    try:
        scrape = Scrape(
            _post_process_func,
            use_proxy=False,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=60,
            call_rate_limit=10,
            randomise_headers=True
        )
        resps = scrape.scrape_all(URLS)
        urls = set(URLS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(urls) else False
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
