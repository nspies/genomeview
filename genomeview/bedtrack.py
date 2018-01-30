import pysam

from genomeview.intervaltrack import Interval, IntervalTrack
from genomeview.utilities import match_chrom_format


# bed_fields = {
#     "chrom": 0,
#     "start"; 1,
# }
    
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
        
        try:
            bed = pysam.TabixFile(self.bed_path)

            chrom = match_chrom_format(chrom, bed.contigs)
            for locus in bed.fetch(chrom, start, end):
                locus = locus.split()
                if not self.include_locus_fn or self.include_locus_fn(locus):
                    yield locus

        except OSError:
            raise NotImplementedError()



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
        if len(interval.locus) < 12:
            yield from super().draw_interval(renderer, interval)
            return
            
        start = self.scale.topixels(interval.start)
        end = self.scale.topixels(interval.end)
        
        row = self.intervals_to_rows[interval.id]
        top = row*(self.row_height+self.margin_y)
        top_thin = top + self.row_height/2 - self.thin_width/2
        midline = top + self.row_height/2 - self.thinnest_width/2
        
        color = self.color_fn(interval)
        temp_label = interval.label
        if interval.label is None:
            temp_label = "{}_{}".format(interval.id, 1 if interval.read.is_read1 else 2)
        
        yield from renderer.rect(start, midline, end-start, self.thinnest_width, fill=color, 
                                 **{"stroke":"none", "id":temp_label})

        # want thick start/end in local coordinates to match block start coords
        thick_start, thick_end = [(int(x) - interval.start) for x in interval.locus[6:8]]

        block_lengths = [int(x) for x in interval.locus[10].strip(",").split(",")]
        block_starts = [int(x) for x in interval.locus[11].strip(",").split(",")]

        assert len(block_lengths) == len(block_starts), \
            "malformed bed line: {}".format("\t".join(interval.locus))

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
            yield from renderer.text(end+self.label_distance, top+self.row_height-2, interval.label, anchor="start")
        