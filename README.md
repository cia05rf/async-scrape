# Async-scrape
## _Perform webscrape asyncronously_

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Async-scrape is a package which uses asyncio and aiohttp to scrape websites and has useful features built in.

## Features

- Breaks - pause scraping when a website blocks your requests consistently
- Rate limit - slow down scraping to prevent being blocked


## Installation

Async-scrape requires [C++ Build tools](https://go.microsoft.com/fwlink/?LinkId=691126) v15+ to run.


```
pip install async-scrape
```

## How to use it
Key inpur parameters:
- `post_process_func` - the callable used to process the returned response
- `post_process_kwargs` - and kwargs to be passed to the callable
- `use_proxy` - should a proxy be used (if this is true then either provide a `proxy` or `pac_url` variable)
- `attempt_limit` - how manay attempts should each request be given before it is marked as failed
- `rest_wait` - how long should the programme pause between loops
- `call_rate_limit` - limits the rate of requests (useful to stop getting blocked from websites)
- `randomise_headers` - if set to `True` a new set of headers will be generated between each request

### Get requests
```
# Create an instance
from async_scrape import AsyncScrape

def post_process(html, resp, **kwargs):
    """Function to process the gathered response from the request"""
    if resp.status == 200:
        return "Request worked"
    else:
        return "Request failed"

async_Scrape = AsyncScrape(
    post_process_func=post_process,
    post_process_kwargs={},
    fetch_error_handler=None,
    use_proxy=False,
    proxy=None,
    pac_url=None,
    acceptable_error_limit=100,
    attempt_limit=5,
    rest_between_attempts=True,
    rest_wait=60,
    call_rate_limit=None,
    randomise_headers=True
)

urls = [
    "https://www.google.com",
    "https://www.bing.com",
]

resps = async_Scrape.scrape_all(urls)
```

### Post requests
```
# Create an instance
from async_scrape import AsyncScrape

def post_process(html, resp, **kwargs):
    """Function to process the gathered response from the request"""
    if resp.status == 200:
        return "Request worked"
    else:
        return "Request failed"

async_Scrape = AsyncScrape(
    post_process_func=post_process,
    post_process_kwargs={},
    fetch_error_handler=None,
    use_proxy=False,
    proxy=None,
    pac_url=None,
    acceptable_error_limit=100,
    attempt_limit=5,
    rest_between_attempts=True,
    rest_wait=60,
    call_rate_limit=None,
    randomise_headers=True
)

urls = [
    "https://eos1jv6curljagq.m.pipedream.net",
    "https://eos1jv6curljagq.m.pipedream.net",
]
payloads = [
    {"value": 0},
    {"value": 1}
]

resps = async_Scrape.scrape_all(urls, payloads=payloads)
```

### Response
Response object is a list of dicts in the format:
```
{
    "url":url, # url of request
    "req":req, # combination of url and params
    "func_resp":func_resp, # response from post processing function
    "status":resp.status, # http status
    "error":None # any error encountered
}
```


## License

MIT

**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
