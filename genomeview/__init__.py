__version__ = "1.0b1"

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
from genomeview.bedtrack import BEDTrack
from genomeview.graphtrack import *
from genomeview.intervaltrack import *

from genomeview.export import render_to_file, save

from genomeview.convenience import visualize_data
from genomeview.utilities import get_one_track