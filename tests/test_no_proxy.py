import pytest
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

kwargs = dict(use_proxy=False)


def test_async_scrape_no_proxy_no_payload():
    return _test_async_scrape_no_payload(**kwargs)


def test_async_scrape_no_proxy_payload():
    return _test_async_scrape_payload(**kwargs)


def test_async_scrape_no_proxy_call_rate_limited():
    return _test_async_scrape_call_rate_limited(**kwargs)


def test_scrape_no_proxy_no_payload():
    return _test_scrape_no_payload(**kwargs)


def test_scrape_no_proxy_payload():
    return _test_scrape_payload(**kwargs)


def test_scrape_all_no_proxy():
    return _test_scrape_all(**kwargs)


def test_scrape_all_no_proxy_call_rate_limited():
    return _test_scrape_all_call_rate_limited(**kwargs)


def test_scrape_one_no_proxy():
    return _test_scrape_one(**kwargs)
