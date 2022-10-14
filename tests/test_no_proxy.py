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
        'https://www.google.com/search?q=yahoo',
        'https://www.google.com/search?q=porn',
        'https://www.google.com/search?q=nba+scores',
        'https://www.google.com/search?q=target',
        'https://www.google.com/search?q=twitter',
        'https://www.google.com/search?q=wordle',
        'https://www.google.com/search?q=instagram',
        'https://www.google.com/search?q=google+docs',
        'https://www.google.com/search?q=walmart',
        'https://www.google.com/search?q=craigslist',
        'https://www.google.com/search?q=fox+news',
        'https://www.google.com/search?q=lakers',
        'https://www.google.com/search?q=cnn',
        'https://www.google.com/search?q=news',
        'https://www.google.com/search?q=netflix',
        'https://www.google.com/search?q=amazon+prime',
        'https://www.google.com/search?q=onlyfans',
        'https://www.google.com/search?q=calculator',
        'https://www.google.com/search?q=ufc',
        'https://www.google.com/search?q=zillow',
        'https://www.google.com/search?q=nfl+scores',
        'https://www.google.com/search?q=restaurants+near+me',
        'https://www.google.com/search?q=costco',
        'https://www.google.com/search?q=bitcoin+price',
        'https://www.google.com/search?q=speed+test',
        'https://www.google.com/search?q=google+flights',
        'https://www.google.com/search?q=espn',
        'https://www.google.com/search?q=dominos',
        'https://www.google.com/search?q=etsy',
        'https://www.google.com/search?q=mlb',
        'https://www.google.com/search?q=google+drive',
        'https://www.google.com/search?q=reddit',
        'https://www.google.com/search?q=best+buy',
        'https://www.google.com/search?q=paypal',
        'https://www.google.com/search?q=indeed',
        'https://www.google.com/search?q=warriors',
        'https://www.google.com/search?q=shein',
        'https://www.google.com/search?q=wells+fargo',
        'https://www.google.com/search?q=roblox',
        'https://www.google.com/search?q=maps',
        'https://www.google.com/search?q=airbnb',
        'https://www.google.com/search?q=ukraine',
        'https://www.google.com/search?q=linkedin',
        'https://www.google.com/search?q=hbo+max',
        'https://www.google.com/search?q=amber+heard',
        'https://www.google.com/search?q=bank+of+america',
        'https://www.google.com/search?q=trump',
        'https://www.google.com/search?q=dodgers',
        'https://www.google.com/search?q=at',
        'https://www.google.com/search?q=weather+tomorrow',
        'https://www.google.com/search?q=facebook+login',
        'https://www.google.com/search?q=chaturbate',
        'https://www.google.com/search?q=macys',
        'https://www.google.com/search?q=gabby+petito',
        'https://www.google.com/search?q=lowes',
        'https://www.google.com/search?q=s',
        'https://www.google.com/search?q=premier+league',
        'https://www.google.com/search?q=credit+karma',
        'https://www.google.com/search?q=xhamster',
        'https://www.google.com/search?q=facebook+marketplace',
        'https://www.google.com/search?q=usps',
        'https://www.google.com/search?q=dow+jones',
        'https://www.google.com/search?q=cvs',
        'https://www.google.com/search?q=ikea',
        'https://www.google.com/search?q=nba+games',
        'https://www.google.com/search?q=brian+laundrie',
        'https://www.google.com/search?q=celtics',
        'https://www.google.com/search?q=chase',
        'https://www.google.com/search?q=traductor',
        'https://www.google.com/search?q=hulu',
        'https://www.google.com/search?q=johnny+depp',
        'https://www.google.com/search?q=capital+one',
        'https://www.google.com/search?q=h',
        'https://www.google.com/search?q=bitcoin',
        'https://www.google.com/search?q=mcdonalds',
        'https://www.google.com/search?q=hotmail',
        'https://www.google.com/search?q=youtube+to+mp3',
        'https://www.google.com/search?q=american+airlines',
        'https://www.google.com/search?q=disney+plus',
        'https://www.google.com/search?q=mlb+scores',
        'https://www.google.com/search?q=yankees']


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
            rest_wait=60,
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
