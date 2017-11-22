import numpy

from genomeview.utilities import match_chrom_format

class MismatchCounts(object):
    """
    keeps track of how many of each nucleotide (or insertion/deletion) are present at each position
    -> used for the quick consensus mode
    """
    types_to_id = {"A":0, "C":1, "G":2, "T":3, "DEL":5}

    def __init__(self, chrom, start, end):
        self.chrom = chrom
        self.start = start
        self.end = end

        length = end - start
        self.counts = numpy.zeros([6, length])#, dtype="uint8")
        self.insertions = numpy.zeros(length)#, dtype="uint8")

    def tally_reads(self, bam):
        depths = []
        for pileupcolumn in bam.pileup(match_chrom_format(self.chrom, bam.references), self.start, self.end, truncate=True):
            depths.append(pileupcolumn.n)
            for pileupread in pileupcolumn.pileups:
                if pileupread.is_refskip:
                    continue
                elif pileupread.is_del:
                    self.add_count(pileupcolumn.pos, "DEL")
                else:
                    nuc =  pileupread.alignment.query_sequence[pileupread.query_position]
                    if nuc != "N":
                        self.add_count(pileupcolumn.pos, nuc)
                if pileupread.indel > 0:
                    self.add_count(pileupcolumn.pos, "INS")

    def add_count(self, position, type_):
        position -= self.start
        if type_ == "INS":
            self.insertions[position] += 1
        else:
            row = self.types_to_id[type_]
            self.counts[row,position] += 1

    # def counts(self, position):
    #     position -= self.start
    #     return self.counts[position,:]

    def query(self, type_, start, end=None):
        if start < self.start or start >= self.end:
            return False

        start -= self.start
        if end is None:
            end = start
        else:
            end -= self.start

        total = self.counts[:,start:(end+1)].sum(axis=0)
        total = total.astype(float)

        if (type_ == "INS"):
            insertions = self.insertions[start:(end+1)]
            if (insertions.sum() / total.sum()) > 0.2:
               return True

        else:        
            row = self.types_to_id[type_]
            this_type = self.counts[row,start:(end+1)]

            if type_ == "DEL":
                if  ((this_type / total) > 0.3).any():
                    return True
            elif ((this_type / total) > 0.2).any():
                return True

        return False
