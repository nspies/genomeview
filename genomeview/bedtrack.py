import logging
import math
import numpy

from genomeview.intervaltrack import Interval, IntervalTrack
from genomeview.utilities import match_chrom_format


# bed_fields = {
#     "chrom": 0,
#     "start"; 1,
# }
    
def fetch(path, chrom, start, end):
    try:
        yield from fetch_from_tabix(path, chrom, start, end)
        return
    except:
        pass

    try:
        yield from fetch_from_bigbed(path, chrom, start, end)
        return
    except:
        pass

    try:
        yield from fetch_from_plainbed(path, chrom, start, end)
        return
    except:
        raise
        pass

    raise NotImplementedError("Not sure how to handle this file: {}".format(path))


def fetch_from_tabix(path, chrom, start, end):
    import pysam

    bed = pysam.TabixFile(path)

    chrom = match_chrom_format(chrom, bed.contigs)
    for locus in bed.fetch(chrom, start, end):
        locus = locus.split()
        yield locus

def fetch_from_bigbed(path, chrom, start, end):
    import pyBigWig

    bed = pyBigWig.open(path)
    assert bed.isBigBed(), "Oops, for some reason I was expecting a bed file: {}".format(path)

    chrom = match_chrom_format(chrom, bed.chroms().keys())
    for cur_start, cur_end, bed_line in bed.entries(chrom, start, end):
        bed_line = bed_line.split()
        yield [chrom, cur_start, cur_end] + bed_line

def fetch_from_plainbed(path, chrom, start, end):
    found_chrom = False
    for line in open(path):
        fields = line.strip().split()
        if fields[0] != chrom: continue
        found_chrom = True

        cur_start, cur_end = fields[1:3]
        if int(cur_end) < start or int(cur_start) > end: continue
        yield fields

    if not found_chrom:
        warning = "Didn't find chromosome {}; make sure it's formatted correctly (eg 'chr1' vs '1')".format(chrom)
        logging.warn(warning)


class BEDTrack(IntervalTrack):
    def __init__(self, bed_path, name=None):
        """
        Args:
            name (str): name of the track
            bed_path (str): path of the bed file to display

        """
        super().__init__([], name=name)
        
        self.bed_path = bed_path
        self.intervals = self

        self.draw_locus_labels = True
        self.include_locus_fn = None

        self.row_height = 12
        self.thick_width = self.row_height
        self.thin_width = 5
        self.thinnest_width = 1

        self.min_exon_width = 1

    def fetch(self):
        """
        iterator over reads from the bam file
        """
        chrom = self.scale.chrom
        start, end = self.scale.start, self.scale.end
        
        for locus in fetch(self.bed_path, chrom, start, end):
            if not self.include_locus_fn or self.include_locus_fn(locus):
                yield locus

    def __iter__(self):
        c = 0
        for i, locus in enumerate(self.fetch()):
            c += 1
            id_ = locus[3] + "_" + str(i)
            chrom = locus[0]
            start = int(locus[1])
            end = int(locus[2])
            strand = locus[5]

            interval = Interval(id_, chrom, start, end, strand)

            interval.locus = locus
            if self.draw_locus_labels:
                interval.label = locus[3]
            yield interval


    def draw_interval(self, renderer, interval):
        interval_pixel_width = self.scale.relpixels(len(interval.locus))
        if interval_pixel_width < 12:
            # could probably improve on this
            yield from super().draw_interval(renderer, interval)
            return
                    
        row = self.intervals_to_rows[interval.id]
        top = row*(self.row_height+self.margin_y)
        top_thin = top + self.row_height/2 - self.thin_width/2
        midline = top + self.row_height/2 - self.thinnest_width/2
        
        color = self.color_fn(interval)
        temp_label = interval.label
        if interval.label is None:
            temp_label = "{}_{}".format(interval.id, 1 if interval.read.is_read1 else 2)
        
        # want thick start/end in local coordinates to match block start coords
        thick_start, thick_end = [(int(x) - interval.start) for x in interval.locus[6:8]]

        block_lengths = [int(x) for x in interval.locus[10].strip(",").split(",")]
        block_starts = [int(x) for x in interval.locus[11].strip(",").split(",")]

        assert len(block_lengths) == len(block_starts), \
            "malformed bed line: {}".format("\t".join(interval.locus))

        # Draw the thin lines between "exons", along with arrows pointing in transcript direction
        for i in range(len(block_starts)-1):
            cur_start = self.scale.topixels(interval.start + block_starts[i] + block_lengths[i])
            cur_end = self.scale.topixels(interval.start + block_starts[i+1])

            direction = "right" if interval.strand=="+" else "left"
            n_arrows = int(round((cur_end-cur_start) / (self.row_height*0.75)))
            arrows = (numpy.arange(1, n_arrows+1) / (n_arrows+1))# * 0.8 + 0.1

            yield from renderer.line_with_arrows(cur_start, midline, cur_end, midline,
                direction=direction, color=color, arrows=arrows, filled=False,
                arrow_scale=self.thinnest_width*0.4, arrowKwdArgs={"stroke-width":self.thinnest_width*0.75})

        # Draw the "exons", both thin (non-coding/UTR) and thick (coding)
        for which in ["thin", "thick"]:
            for cur_start, length in zip(block_starts, block_lengths):
                cur_end = cur_start + length

                if which == "thick":
                    cur_y = top
                    cur_width = self.thick_width

                    if cur_end < thick_start: continue
                    if cur_start > thick_end: continue
                    cur_start = max(thick_start, cur_start)
                    cur_end = min(thick_end, cur_end)
                else:
                    if (cur_start > thick_start) and (cur_end < thick_end): continue

                    cur_y = top_thin
                    cur_width = self.thin_width

                cur_start = self.scale.topixels(interval.start + cur_start)
                cur_end = self.scale.topixels(interval.start + cur_end)
                width = cur_end - cur_start

                if width < self.min_exon_width:
                    cur_start -= self.min_exon_width / 2
                    width = self.min_exon_width


                yield from renderer.rect(cur_start, cur_y, width, cur_width, fill=color, 
                                         **{"stroke":"none", "id":temp_label})


        if interval.label is not None:
            end = self.scale.topixels(interval.end)

            yield from renderer.text(end+self.label_distance, top+self.row_height-2, interval.label, anchor="start")
        