Welcome to genomeview's documentation!
======================================

.. toctree::
   :maxdepth: -1
   :caption: Contents:

   overview
   details
   axis
   bams
   rendering
   advanced_usage

What is GenomeView?
===================

GenomeView visualizes genomic data straight from python. Features include:

* Easily extensible
* Integrates with `jupyter notebook <http://jupyter.readthedocs.io/en/latest/index.html>`_ / `jupyterlab <https://github.com/jupyterlab/jupyterlab>`_
* High-quality vector output to standard SVG format
* Includes built-in tracks to visualize:

    * BAMs (short and long reads)

       * Both single-ended and paired-ended views available
       * Includes a cython-optimized quick consensus module to visualize error-prone long-read data
       * Group BAM reads by tag or other features using python callbacks

    * Graphical data such as coverage tracks, wiggle files, etc

The output is suitable for static visualization in screen or print formats. GenomeView is not designed to produce interactive visualizations, although the python interface, through jupyter, provides an easy interface to quickly create new visualizations.


Installation
============

GenomeView requires python 3.3 or greater. The following shell command should typically suffice for installing the latest release:

.. code-block:: bash

    pip install genomeview

Or to install the bleeding edge from github:

.. code-block:: bash

    pip install -U git+https://github.com/nspies/genomeview.git
