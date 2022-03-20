import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="async-scrape",                     # This is the name of the package
    version="0.1.8",                         # The initial release version
    author="Robert Franklin",                     # Full name of the author
    description="Async-scrape is a package which uses asyncio and aiohttp to scrape websites and has useful features built in.",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.8',                # Minimum version requirement of the package
    py_modules=["async-scrape"],            # Name of the python package
    install_requires=[
        "python>=3.8",
        "nest-asyncio>=1.5.1",
        "aiohttp>=3.7.4",
        "PyPAC>=0.15.0",
        "requests-html>=0.10.0",
        "pandas>=1.3.2"
    ],                     # Install other dependencies if any
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
)
