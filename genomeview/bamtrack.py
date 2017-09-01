import collections
import pysam

from genomeview.intervaltrack import Interval, IntervalTrack
from genomeview.quickconsensus import MismatchCounts


class SingleEndBAMTrack(IntervalTrack):
    def __init__(self, name, bam_path):
        super().__init__(name, [])
        
        self.bam = pysam.AlignmentFile(bam_path)
        self.intervals = self
        self.mismatch_counts = None
        
        self.nuc_colors = {"A":"blue", "C":"orange", "G":"green", "T":"black", "N":"gray"}
        self.insertion_color = "cyan"
        self.clipping_color = "cyan"
        self.deletion_color = "gray"

        self.quick_consensus = True
        self.draw_mismatches = True
        self.include_secondary = True
        
        self.draw_read_labels = False


    def __iter__(self):
        c = 0
        for read in self.bam.fetch(self.scale.chrom, self.scale.start, self.scale.end):
            c += 1
            if read.is_unmapped: continue
            if read.is_secondary and not self.include_secondary: continue
            id_ = read.query_name 
            interval = Interval(id_, self.scale.chrom, read.reference_start, read.reference_end, 
                                not read.is_reverse)
            interval.read = read
            if self.draw_read_labels:
                interval.label = read.query_name
            yield interval
        print(c)

    def layout(self, scale):
        super().layout(scale)
        self.reset_mismatch_counts()

    def reset_mismatch_counts(self):
        if self.quick_consensus and self.draw_mismatches:
            self.mismatch_counts = MismatchCounts(self.scale.chrom, self.scale.start, self.scale.end)
            self.mismatch_counts.tally_reads(self.bam)

    def layout_interval(self, interval):
        super().layout_interval(interval)

    def draw_interval(self, renderer, interval):
        yield from super().draw_interval(renderer, interval)

        if self.draw_mismatches:
            yield from self._draw_cigar(renderer, interval.read)

    def _draw_cigar(self, renderer, read):
        if read.is_secondary: return
        
        min_width = 2
        row = self.intervals_to_rows[read.query_name]
        yoffset = row*(self.row_height+self.margin_y)

        genome_position = read.reference_start
        sequence_position = 0
        alnseq = read.query_sequence

        extras = {"stroke":"none"}

        for code, length in read.cigartuples:
            length = int(length)
            if code == 0: #"M":
                for i in range(length):
                    if genome_position+i < self.scale.start: continue
                    if genome_position+i >= self.scale.end: break

                    alt = alnseq[sequence_position+i]
                    ref = self.scale.get_seq(genome_position+i, genome_position+i+1)

                    if alt != ref:
                        curstart = self.scale.topixels(genome_position+i)
                        curend = self.scale.topixels(genome_position+i+1)

                        color = self.nuc_colors[alnseq[sequence_position+i]]

                        if not self.mismatch_counts or alt=="N" or self.mismatch_counts.query(alt, genome_position+i):
                            width = max(curend-curstart, min_width)
                            midpoint = (curstart+curend)/2
                            yield from renderer.rect(midpoint-width/2, yoffset, width, self.row_height, fill=color, 
                                                     **extras)

                sequence_position += length
                genome_position += length
            elif code == 2: #in "D":
                if not self.mismatch_counts or self.mismatch_counts.query("DEL", genome_position, genome_position+length+1):
                    curstart = self.scale.topixels(genome_position)
                    curend = self.scale.topixels(genome_position+length+1)
                    yield from renderer.rect(curstart, yoffset, curend-curstart, self.row_height, fill=self.deletion_color, 
                                             **extras)

                genome_position += length
            elif code == 1: # I
                if not self.mismatch_counts or self.mismatch_counts.query("INS", genome_position-2, genome_position+2):
                    curstart = self.scale.topixels(genome_position-0.5)
                    curend = self.scale.topixels(genome_position+0.5)

                    width = max(curend-curstart, min_width)
                    midpoint = (curstart+curend)/2

                    yield from renderer.rect(midpoint-width/2, yoffset, width, self.row_height, fill=self.insertion_color,
                                             **extras)
                sequence_position += length
            elif code in [4, 5]: #"HS":
                if length >= 5:
                    # always draw clipping, irrespective of consensus sequence or mode
                    curstart = self.scale.topixels(genome_position-0.5)
                    curend = self.scale.topixels(genome_position+0.5)

                    width = max(curend-curstart, min_width*2)
                    midpoint = (curstart+curend)/2

                    yield from renderer.rect(midpoint-width/2, yoffset, width, self.row_height, fill=self.clipping_color,
                                             **extras)

                if code == 4:
                    sequence_position += length




class PairedEndBAMTrack(SingleEndBAMTrack):
    def __init__(self, name, bam_path):
        super().__init__(name, bam_path)

        self.overlap_color = "lime"

    def layout(self, scale):
        if scale == self.scale: return
        
        self.scale = scale
        self.reset_mismatch_counts()
        
        # for chrom, start, end in self.scale.regions():
        chrom, start, end = self.scale.chrom, self.scale.start, self.scale.end
        cur_read_coords = collections.defaultdict(list)

        for read in self.bam.fetch(chrom, start, end):
            if read.is_unmapped: continue
            cur_read_coords[read.query_name].append(
                (read.reference_start, read.reference_end, read.next_reference_start, read.is_proper_pair))
        
        # a bit of hocus-pocus to deal with reads whose mates map outside of our region of interest
        for pair in cur_read_coords.values():
            if len(pair) == 1:
                read_end = pair[0]
                if read_end[3]:
                    pair.append((read_end[2], read_end[2]))
                pair.sort()

        for read_name, coords in sorted(cur_read_coords.items(), key=lambda x: x[1]):
            pair_start = coords[0][0]
            pair_end = coords[-1][1]
            interval = Interval(read_name, chrom, pair_start, pair_end)
            if self.draw_read_labels:
                interval.label = read_name
            self.layout_interval(interval)
            #self.intervals.append(interval)
                
        self.height = (len(self.rows)+1) * (self.row_height+self.margin_y)
    
    
    def draw_read_pair(self, renderer, reads):
        reads = [read for read in reads if not read.is_unmapped]
        if len(reads) == 0: return

        chrom = reads[0].reference_name
        row = self.intervals_to_rows[reads[0].query_name]
        
        pair_start = None
        if len(reads) > 1:
            pair_start = reads[0].reference_end
            pair_end = reads[-1].reference_start
        elif reads[0].is_proper_pair:
            # some more hocus-pocus to deal with reads whose mates map outside of our region of interest
            if reads[0].next_reference_start < reads[0].reference_start:
                pair_start = reads[0].next_reference_start
                pair_end = reads[0].reference_start
            else:
                pair_start = reads[0].reference_start
                pair_end = reads[0].next_reference_start

        if pair_start is not None:
            x1 = self.scale.topixels(pair_start)
            x2 = self.scale.topixels(pair_end)
            y = row*(self.row_height+self.margin_y) + self.row_height/2 # refactor

            yield from renderer.line(x1, y, x2, y, **{"stroke-width":1, "stroke":"gray"})
        
        for i, read_end in enumerate(reads):
            interval = Interval(read_end.query_name, chrom, read_end.reference_start,
                                read_end.reference_end, not read_end.is_reverse)
            interval.read = read_end
            yield from self.draw_interval(renderer, interval)

            if i == 1 and self.draw_read_labels:
                end = self.scale.topixels(read_end.reference_end)
                top = row*(self.row_height+self.margin_y)

                yield from renderer.text(end+self.label_distance, top+self.row_height,
                                         read_end.query_name, anchor="start")

            
    def render(self, renderer):
        # for chrom, start, end in self.scale.regions():

        read_buffer = {}
        for read in self.bam.fetch(self.scale.chrom, self.scale.start, self.scale.end):
            if read.is_unmapped: continue
            if read.query_name in read_buffer:
                other_read = read_buffer.pop(read.query_name)
                cur_reads = [other_read, read]
            else:
                read_buffer[read.query_name] = read
                continue
            
            for read_end in cur_reads:
                yield from self.draw_read_pair(renderer, cur_reads)
                
        for read_name, read in read_buffer.items():
            yield from self.draw_read_pair(renderer, [read])
        
        for x in  self.render_label(renderer):
            yield x
