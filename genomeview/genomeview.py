import collections


from genomeview.svg import Renderer, SVG


class Document:
    header = """<svg version="1.1" baseProfile="full" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">"""
    footer = """</svg>"""
        
    def __init__(self, width):
        self.elements = []
        self.width = width
        self.renderer = SVG()
        
        self.margin_x = 5
        self.margin_y = 5

        self.between_views = 5

    def add_view(self, view):
        self.elements.append(view)
        
    def get_tracks(self, name=None):
        matching = []
        for element in self.elements:
            try:
                matching.extend(element.get_tracks(name))
            except AttributeError:
                pass
        return matching

    def layout(self):
        self.view_width = self.width - self.margin_x*2
        for element in self.elements:
            element.layout(self.view_width)
        
    def render(self):
        self.layout()
        
        total_height = sum(element.height+self.between_views for element in self.elements) + self.margin_y*2
        yield self.header.format(height=total_height, width=self.width)
        
        cury = self.margin_y
        for element in self.elements:
            renderer = Renderer(self.renderer, self.margin_x, cury, self.view_width, element.height)
            yield from renderer.render(element)
            cury += element.height + self.between_views
            
        yield self.footer
        
    def _repr_svg_(self):
        return "\n".join(self.render())
        
class ViewRow:
    def __init__(self, name=None):
        self.name = name
        self.views = []

        self.width = None
        self.height = None

        self.space_between = 5
    
    def add_view(self, view):
        self.views.append(view)
    
    def get_views(self, name=None):
        matching = []
        for view in self.views:
            if name is None or view.name==name:
                matching.extend(view)
        return matching

    def get_tracks(self, name=None):
        matching = []
        for view in self.views:
            try:
                matching.extend(view.get_tracks(name))
            except AttributeError:
                pass
        return matching

    def layout(self, width):
        self.width = width
        n_views = len(self.views)
        self.each_width = (self.width - self.space_between*(n_views-1)) / n_views

        self.height = 0
        for view in self.views:
            view.layout(self.each_width)
            self.height = max(self.height, view.height)
    
    def render(self, renderer):
        curx = 0
        for view in self.views:
            subrenderer = renderer.subrenderer(x=curx, width=self.each_width, height=view.height)
            yield from subrenderer.render(view)
            curx += self.each_width + self.space_between
        

class GenomeView:
    def __init__(self, chrom, start, end, strand, source=None, name=None):
        self.name = name
        self.tracks = []

        self.scale = Scale(chrom, start, end, strand, source)

        self.pixel_width = None
        self.pixel_height = None

        self.margin_y = 10
    
    def add_track(self, track):
        self.tracks.append(track)

    def get_tracks(self, name=None):
        matching = []
        for track in self.tracks:
            if name is None or track.name == name:
                matching.append(track)
        return matching
        
    def layout(self, width):
        self.pixel_width = width
        self.scale.pixel_width = width

        self.height = 0
        for track in self.tracks:
            track.layout(self.scale)
            self.height += track.height + self.margin_y
    
    def render(self, renderer):
        cury = 0
        for track in self.tracks:
            subrenderer = renderer.subrenderer(y=cury, height=track.height)
            yield from subrenderer.render(track)
            cury += track.height + self.margin_y
        
    
    
class Scale(object):
    """
    Maintains information about a projection of a specific genomic
    interval into screen coordinates.

    That is, we're interested in visualizing an interval (chrom:start-end) 
    on a canvas of a specified pixel width. The scale enables converting
    genomic coordinates into the display coordinates.
    """
    def __init__(self, chrom, start, end, strand, source):
        self.chrom = chrom
        self.start = start
        self.end = end
        self.strand = strand

        self.pixel_width = None
        self._param = None

        self.source = source
        self._seq = None

        if self.start >= self.end:
            raise ValueError("End coordinate must be greater than start coordinate; you specified {}:{}-{}".format(chrom, start, end))

    def _setup(self):
        if self._param == self.pixel_width: return
        self._param = self.pixel_width
        self._seq = None

        nt_width = self.end - self.start
        
        self.bases_per_pixel = nt_width / self.pixel_width

    def topixels(self, genomic_position):
        """
        Converts a genomic position to a pixel location in the current
        coordinate system.
        """
        self._setup()

        pos = (genomic_position - self.start) / float(self.bases_per_pixel)
        return pos

    def relpixels(self, genomic_size):
        """
        Takes a genomic length (ie, a number of basepairs) and converts
        it to a relative screen length in pixels.
        """
        self._setup()

        dist = genomic_size / float(self.bases_per_pixel)
        return dist
    
    def get_seq(self, start=None, end=None, strand="+"):
        """
        Gets the nucleotide sequence of an interval. By default, returns the 
        sequence for the current genomic interval.
        """
        self._setup()

        assert self.source is not None

        if start is None:
            start = self.start
        if end is None:
            end = self.end
        
        assert start >= self.start
        assert end <= self.end

        if self._seq is None:
            self._seq = self.source.get_seq(self.chrom, self.start, self.end, self.strand).upper()

        cur_seq = self._seq[start-self.start:end-self.start]
        if strand != self.strand:
            raise Exception("ack")

        return cur_seq

