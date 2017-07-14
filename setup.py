#!/usr/bin/env python

from setuptools import setup, find_packages

def get_version(string):
    """ Parse the version number variable __version__ from a script. """
    import re
    version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_str = re.search(version_re, string, re.M).group(1)
    return version_str


setup(name="genomeview",
      version=get_version(open('genomeview/__init__.py').read()),
      description="genomeview",
      author="Noah Spies",
      packages=find_packages(),
      #entry_points={"console_scripts": ["genosv = genosv.app.main:main"]},
      install_requires=[], 
     )
