import pytest
import os
from tests._tests import (
    _test_async_scrape_no_payload,
    _test_async_scrape_payload,
    _test_async_scrape_call_rate_limited,
    _test_scrape_no_payload,
    _test_scrape_payload,
    _test_scrape_all,
    _test_scrape_all_call_rate_limited,
    _test_scrape_one,
)

kwargs = dict(use_proxy=True, proxy=None, pac_url=os.environ["pac_url"])


def test_async_scrape_proxy_no_payload():
    return _test_async_scrape_no_payload(**kwargs)


def test_async_scrape_proxy_payload():
    return _test_async_scrape_payload(**kwargs)


def test_async_scrape_proxy_call_rate_limited():
    return _test_async_scrape_call_rate_limited(**kwargs)


def test_scrape_proxy_no_payload():
    return _test_scrape_no_payload(**kwargs)


def test_scrape_proxy_payload():
    return _test_scrape_payload(**kwargs)


def test_scrape_all_proxy():
    return _test_scrape_all(**kwargs)


def test_scrape_all_proxy_call_rate_limited():
    return _test_scrape_all_call_rate_limited(**kwargs)


def test_scrape_one_proxy():
    return _test_scrape_one(**kwargs)
