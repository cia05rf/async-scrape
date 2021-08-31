from distutils.core import setup
setup(
  name = 'async-scrape',         # How you named your package folder (MyLib)
  packages = [
    'async_scrape',
    'async_scrape/libs'
    ],   # Chose the same as "name"
  version = '0.1.3',      # Start with a small number and increase it with every change you make
  license = 'MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A package designed to scrape webpages using aiohttp and asyncio. Has some error handling to overcome common issues such as sites blocking you after n requests over a short period.',   # Give a short description about your library
  author = 'Robert Franklin',                   # Type in your name
  author_email = 'cia05rf@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/cia05rf/async-scrape/',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/cia05rf/async-scrape/archive/refs/tags/v0.1.0.tar.gz',    # I explain this later on
  keywords = [],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
        "asyncio",
        "nest-asyncio",
        "aiohttp",
        "PyPAC",
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.9',      #Specify which pyhton versions that you want to support
  ],
)