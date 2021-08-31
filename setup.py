from distutils.core import setup
setup(
  name = 'async-scrape',
  packages = [
    'async_scrape',
    'async_scrape/libs'
    ],
  version = '0.1.3',
  license = 'MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A package designed to scrape webpages using aiohttp and asyncio. Has some error handling to overcome common issues such as sites blocking you after n requests over a short period.',   # Give a short description about your library
  author = 'Robert Franklin',
  author_email = 'cia05rf@gmail.com',
  url = 'https://github.com/cia05rf/async-scrape/',
  download_url = 'https://github.com/cia05rf/async-scrape/archive/refs/tags/v0.1.0.tar.gz',
  keywords = [],
  install_requires=[
        "asyncio",
        "nest-asyncio",
        "aiohttp",
        "PyPAC",
        "requests-html",
        "pandas"
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Pick a license
    'Programming Language :: Python :: 3.9',      # Specify which pyhton versions that you want to support
  ],
)