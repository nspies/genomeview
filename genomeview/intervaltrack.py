from genomeview.track import Track

class Interval:
    def __init__(self, id_, chrom, start, end, strand="+", label=None):
        self.chrom = chrom
        self.start = start
        self.end = end
        self.id = id_
        self.label = label
        
        if isinstance(strand, bool):
            strand = {True:"+", False:"-"}[strand]
        self.strand = strand

    def overlaps(self, other, ignore_strand=True):
        if self.chrom != other.chrom:
            return False
        if other.start > self.end or self.start > other.end:
            return False
        if not ignore_strand and self.strand != other.strand:
            return False
        return True

    def __repr__(self):
        return "{}:{:,}-{:,}{}".format(self.chrom, self.start, self.end, self.strand)
        
def color_by_strand(interval):
    # brightness = 0.2 + (cur_reads[0].mapq/40.0*0.8)
    color = "#E89E9D"
    if interval.strand == "-":
        color = "#8C8FCE"
    return color
    


class IntervalTrack(Track):
    def __init__(self, intervals, name=None):
        super().__init__(name)
        self.rows = []
        self.intervals_to_rows = {}
        
        self.row_height = 8
        self.margin_x = 15
        self.margin_y = 2
        self.label_distance = 3
        
        self.intervals = intervals

        self.color_fn = color_by_strand

    def layout_interval(self, interval):
        row = 0
        interval_start = self.scale.topixels(interval.start)
        for row, row_end in enumerate(self.rows):
            if interval_start > row_end:
                break
        else:
            self.rows.append(None)
            row = len(self.rows) - 1
        
        new_end = self.scale.topixels(interval.end) + self.margin_x
        if interval.label is not None:
            new_end += len(interval.label) * self.row_height * 0.75
        self.rows[row] = new_end

        assert not interval.id in self.intervals_to_rows
        self.intervals_to_rows[interval.id] = row
        

    def layout(self, scale):
        super().layout(scale)

        self.rows = []
        self.intervals_to_rows = {}

        for interval in self.intervals:
            self.layout_interval(interval)
            
        self.height = (len(self.rows)+1) * (self.row_height+self.margin_y)
    
    def draw_interval(self, renderer, interval):
        start = self.scale.topixels(interval.start)
        end = self.scale.topixels(interval.end)
        
        row = self.intervals_to_rows[interval.id]
        top = row*(self.row_height+self.margin_y)
        
        color = self.color_fn(interval)
        temp_label = interval.label
        if interval.label is None:
            temp_label = interval.id

        # yield from renderer.rect(start, top, end-start, self.row_height, fill=color, 
        #     **{"stroke":"none", "id":temp_label})

        arrow_width = min(self.row_height / 2, self.margin_x * 0.7, self.scale.relpixels(30))
        direction = "right" if interval.strand=="+" else "left"

        yield from renderer.block_arrow(start, top, end-start, self.row_height, 
            arrow_width=arrow_width, direction=direction,
            fill=color, **{"stroke":"none", "id":temp_label})

        if interval.label is not None:
            yield from renderer.text(end+self.label_distance, top+self.row_height-2, interval.label, anchor="start")
        
    def render(self, renderer):
        for interval in self.intervals:
            yield from self.draw_interval(renderer, interval)
            
        yield from self.render_label(renderer)
