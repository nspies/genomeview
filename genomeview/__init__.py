__version__ = "0.9.4.2"

from genomeview.genomeview import *
from genomeview.genomesource import *

try:
    from genomeview._quickconsensus import *
except ImportError:
    import logging
    logging.warn("Unable to load cythonized quickconsensus module; "
                 "drawing reads using quick consensus mode will be "
                 "substantially slower")
    from genomeview.quickconsensus import *

from genomeview.axis import *
from genomeview.track import *
from genomeview.bamtrack import *
from genomeview.graphtrack import *
from genomeview.intervaltrack import *

from genomeview.utilities import render_to_file
