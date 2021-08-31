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
Create an object for either `AsyncScrape` or `Scrape` (if you want to work synchronously).

Collect your urls and then pass them to the `scrape_all` method.

A post processing functionMUST be provided. This will process the html and response object once it has been received.
The post processing object must have arguments for `html` and `resp`.
A set of fixed kwargs can be passed to the post processing function with `post_process_kwargs` argument when setting up the object (obviously this can be set to another value at any time).
```
#Create an instance
from async_scrape import AsyncScrape

def post_process(resp):
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
    rest_wait=60
)

urls = [
    "https://www.google.com",
    "https://www.bing.com",
]

resps = async_Scrape.scrape_all(urls)
```

Response object is a list of dicts in the format:
```
{
    "url":url, #url of request
    "func_resp":func_resp, #response from post processing function
    "status":resp.status, #http status
    "error":None #any error encountered
}
```

## Proxy
When using a proxy set `use_proxy=True` when creating the `AsyncScrape` or `Scrape` object. Then pass in either:
- `pac_url` - a string for the location of a pac file
- `proxy` - string giving a proxy IP address to use


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
