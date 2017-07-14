import collections


from svg import Renderer, SVG
from genosv.app import genomesource


class Document:
    header = """<svg version="1.1" baseProfile="full" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">"""
    footer = """</svg>"""
        
    def __init__(self, width):
        self.elements = []
        self.width = width
        self.renderer = SVG()
        
    def layout(self):
        for element in self.elements:
            element.layout(self.width)
        
    def render(self):
        self.layout()
        
        total_height = sum(element.height for element in self.elements)
        yield self.header.format(height=total_height, width=self.width)
        
        cury = 0
        for element in self.elements:
            renderer = Renderer(self.renderer, 0, cury, self.width, element.height)
            yield from renderer.render(element)
            cury += element.height + 5
            
        yield self.footer
        
    def _repr_svg_(self):
        return "\n".join(self.render())
        
class ViewRow:
    def __init__(self, name):
        self.name = name
        self.views = collections.OrderedDict()

        self.width = None
        self.height = None
    
    def add_view(self, view):
        assert view.name not in self.views
        self.views[view.name] = view
        
    def layout(self, width):
        self.width = width
        self.each_width = self.width / len(self.views)

        self.height = 0
        for name, view in self.views.items():
            view.layout(self.each_width)
            self.height = max(self.height, view.height)
    
    def render(self, renderer):
        curx = 0
        for name, view in self.views.items():
            subrenderer = renderer.subrenderer(x=curx, width=self.each_width, height=view.height)
            yield from subrenderer.render(view)
            curx += self.each_width
        

class GenomeView:
    def __init__(self, name, chrom, start, end, strand, source):
        self.name = name
        self.tracks = collections.OrderedDict()

        self.scale = Scale(chrom, start, end, strand, source)

        self.pixel_width = None
        self.pixel_height = None
    
    
    def add_track(self, track):
        assert track.name not in self.tracks
        self.tracks[track.name] = track
        
    def layout(self, width):
        self.pixel_width = width
        self.scale.pixel_width = width

        self.height = 0
        for name, track in self.tracks.items():
            track.layout(self.scale)
            self.height += track.height
    
    def render(self, renderer):
        cury = 0
        for name, track in self.tracks.items():
            subrenderer = renderer.subrenderer(y=cury, height=track.height)
            yield from subrenderer.render(track)
            cury += track.height + 5
        
    
    
class Scale(object):
    def __init__(self, chrom, start, end, strand, source):
        self.chrom = chrom
        self.start = start
        self.end = end
        self.strand = strand

        self.pixel_width = None
        self._param = None

        self.source = source
        self._seq = None

    def _setup(self):
        if self._param == self.pixel_width: return
        self._param = self.pixel_width
        self._seq = None

        nt_width = self.end - self.start
        self.bases_per_pixel = nt_width / self.pixel_width

    def topixels(self, g):
        self._setup()

        pos = (g - self.start) / float(self.bases_per_pixel)
        return pos

    def relpixels(self, g):
        self._setup()

        dist = g / float(self.bases_per_pixel)
        return dist
    
    def get_seq(self, start=None, end=None, strand="+"):
        self._setup()

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




if __name__ == "__main__":
    from track import Track
    from bamtrack import PairedEndBAMTrack
    from axis import Axis

    sources = {"genome":genomesource.FastaGenomeSource("/Volumes/frida/nspies/data/bwa-hg19/hg19.fasta")}
    gv = GenomeView("ref", "chr2", 67195617, 67196817, "+", sources["genome"])


    bam_track = PairedEndBAMTrack("/Volumes/frida/nspies/trios/Illumina/HG002_Justin-10953946/HG002run6-19068059/HG002run6_S1.bam")
    gv.add_track(bam_track)

    axis_track = Axis()
    axis_track.name = "axis"
    gv.add_track(axis_track)


    # track = Track()
    # track.name = "tr1"
    # gv.add_track(track)

    gv2 = GenomeView("ref2", "chr2", 67195627, 67196827, "+", sources["genome"])

    bam_track = PairedEndBAMTrack("/Volumes/frida/nspies/trios/Illumina/HG002_Justin-10953946/HG002run6-19068059/HG002run6_S1.bam")
    gv2.add_track(bam_track)

    viewrow = ViewRow("row")
    viewrow.add_view(gv)
    viewrow.add_view(gv2)


    doc = Document(1900)
    doc.elements.append(gv)
    # doc.elements.append(viewrow)
    with open("temp.svg", "w") as f:
        f.write(doc._repr_svg_())

    import subprocess
    subprocess.check_call("open -a /Applications/Firefox.app temp.svg", shell=True)

