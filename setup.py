#!/usr/bin/env python

from setuptools import setup, find_packages, Extension

def get_version(string):
    """ Parse the version number variable __version__ from a script. """
    import re
    version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_str = re.search(version_re, string, re.M).group(1)
    return version_str


def get_includes():
    class Includes:
        def __iter__(self):
            import pysam
            import numpy
            return iter(pysam.get_include()+[numpy.get_include()])
        def __getitem__(self, i):
            return list(self)[i]
    return Includes()

def get_defines():
    class Defines:
        def __iter__(self):
            import pysam
            return iter(pysam.get_defines())
        def __getitem__(self, i):
            return list(self)[i]
    return Defines()


setup(name="genomeview",
      version=get_version(open('genomeview/__init__.py').read()),
      description="genomeview",
      author="Noah Spies",
      packages=find_packages(),

      setup_requires=["cython", "pysam", "numpy"],
      install_requires=["pysam", "numpy"], 
      ext_modules = [
          Extension("genomeview._quickconsensus",
                  sources=["genomeview/_quickconsensus.pyx"],
                  include_dirs=get_includes(),
                  define_macros=get_defines()
                  )
          ],
      python_requires=">=3.3"
     )
