import traceback
import logging

from async_scrape import AsyncScrape
from async_scrape import Scrape

# Hardcoded urls for testing
GET_URLS = [
    'https://www.google.com/search?q=weather',
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
    'https://www.google.com/search?q=yahoo'
]

POST_URLS = [
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net"
]

PAYLOADS = [
    {'value': 0},
    {'value': 1},
    {'value': 2},
    {'value': 3},
    {'value': 4},
    {'value': 5},
    {'value': 6},
    {'value': 7},
    {'value': 8},
    {'value': 9},
    {'value': 10},
    {'value': 11},
    {'value': 12},
    {'value': 13},
    {'value': 14},
    {'value': 15},
    {'value': 16},
    {'value': 17},
    {'value': 18},
    {'value': 19}
]


def _post_process_func(html, resp):
    return "Hello world"


def _test_async_scrape_no_payload(
    use_proxy: bool = False,
    pac_url: str = None
    ):
    try:
        async_scrape = AsyncScrape(
            _post_process_func,
            use_proxy=use_proxy,
            pac_url=pac_url,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=60,
            call_rate_limit=None,
            randomise_headers=True
        )
        resps = async_scrape.scrape_all(GET_URLS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(GET_URLS) else False
    except Exception as e:
        result = False
    assert result is True


def _test_async_scrape_payload(
    use_proxy: bool = False,
    pac_url: str = None
    ):
    try:
        async_scrape = AsyncScrape(
            _post_process_func,
            use_proxy=use_proxy,
            pac_url=pac_url,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=10,
            call_rate_limit=None,
            randomise_headers=True
        )
        resps = async_scrape.scrape_all(POST_URLS, payloads=PAYLOADS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(POST_URLS) else False
    except Exception as e:
        result = False
    assert result is True


def _test_async_scrape_call_rate_limited(
    use_proxy: bool = False,
    pac_url: str = None
    ):
    try:
        async_scrape = AsyncScrape(
            _post_process_func,
            use_proxy=use_proxy,
            pac_url=pac_url,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=10,
            call_rate_limit=10,
            randomise_headers=True
        )
        resps = async_scrape.scrape_all(GET_URLS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(GET_URLS) else False
    except Exception as e:
        result = False
    assert result is True


def _test_scrape_no_payload(
    use_proxy: bool = False,
    pac_url: str = None
    ):
    try:
        scrape = Scrape(
            _post_process_func,
            use_proxy=use_proxy,
            pac_url=pac_url,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=10,
            call_rate_limit=None,
            randomise_headers=True
        )
        resps = scrape.scrape_all(GET_URLS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(GET_URLS) else False
    except Exception as e:
        logging.error(traceback.format_exc())
        result = False
    assert result is True


def _test_scrape_payload(
    use_proxy: bool = False,
    pac_url: str = None
    ):
    try:
        scrape = Scrape(
            _post_process_func,
            use_proxy=use_proxy,
            pac_url=pac_url,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=10,
            call_rate_limit=None,
            randomise_headers=True
        )
        resps = scrape.scrape_all(POST_URLS, payloads=PAYLOADS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(POST_URLS) else False
    except Exception as e:
        logging.error(traceback.format_exc())
        result = False
    assert result is True


def _test_scrape_all(
    use_proxy: bool = False,
    pac_url: str = None
    ):
    try:
        scrape = Scrape(
            _post_process_func,
            use_proxy=use_proxy,
            pac_url=pac_url,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=10,
            call_rate_limit=None,
            randomise_headers=True
        )
        resps = scrape.scrape_all(GET_URLS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(GET_URLS) else False
    except Exception as e:
        logging.error(traceback.format_exc())
        result = False
    assert result is True


def _test_scrape_all_call_rate_limited(
    use_proxy: bool = False,
    pac_url: str = None
    ):
    try:
        scrape = Scrape(
            _post_process_func,
            use_proxy=use_proxy,
            pac_url=pac_url,
            consecutive_error_limit=100,
            attempt_limit=5,
            rest_between_attempts=True,
            rest_wait=10,
            call_rate_limit=10,
            randomise_headers=True
        )
        resps = scrape.scrape_all(GET_URLS)
        success = [False if r["error"] else True for r in resps]
        result = True if len(success) == len(GET_URLS) else False
    except Exception as e:
        logging.error(traceback.format_exc())
        result = False
    assert result is True


def _test_scrape_one(
    use_proxy: bool = False,
    pac_url: str = None
    ):
    try:
        scrape = Scrape(
            _post_process_func,
            use_proxy=use_proxy,
            pac_url=pac_url,
            attempt_limit=1
        )
        resps = scrape.scrape_one(GET_URLS[0])
        result = True if resps["status"] else False
    except Exception as e:
        logging.error(traceback.format_exc())
        result = False
    assert result is True
