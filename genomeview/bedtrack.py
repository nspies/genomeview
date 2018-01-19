import pysam

from genomeview.intervaltrack import Interval, IntervalTrack
from genomeview.utilities import match_chrom_format


# bed_fields = {
#     "chrom": 0,
#     "start"; 1,
# }
    
class BEDTrack(IntervalTrack):
    def __init__(self, name, bed_path):
        """
        Args:
            name (str): name of the track
            bed_path (str): path of the bed file to display

        """
        super().__init__(name, [])
        
        self.bed_path = bed_path
        self.intervals = self

        self.draw_locus_labels = True
        self.include_locus_fn = None

        self.thick_width = self.row_height
        self.thin_width = 3

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
        
        color = self.color_fn(interval)
        temp_label = interval.label
        if interval.label is None:
            temp_label = "{}_{}".format(interval.id, 1 if interval.read.is_read1 else 2)
        
        yield from renderer.rect(start, top_thin, end-start, self.thin_width, fill=color, 
                                 **{"stroke":"none", "id":temp_label})

        thick_lengths = [int(x) for x in interval.locus[10].strip(",").split(",")]
        thick_starts = [int(x) for x in interval.locus[11].strip(",").split(",")]

        assert len(thick_lengths) == len(thick_starts), \
            "malformed bed line: {}".format("\t".join(interval.locus))

        for cur_start, length in zip(thick_starts, thick_lengths):
            cur_start = start + self.scale.relpixels(cur_start)
            width = self.scale.relpixels(length)
            if width < self.min_exon_width:
                cur_start -= self.min_exon_width / 2
                width = self.min_exon_width


            yield from renderer.rect(cur_start, top, width, self.thick_width, fill=color, 
                                     **{"stroke":"none", "id":temp_label})


        if interval.label is not None:
            yield from renderer.text(end+self.label_distance, top+self.row_height-2, interval.label, anchor="start")
        