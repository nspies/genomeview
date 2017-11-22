import numpy

from libc.stdint cimport uint32_t, uint8_t, uint64_t, int64_t
from cpython cimport PyBytes_FromStringAndSize

from pysam.libcalignmentfile cimport AlignmentFile, AlignedSegment, IteratorRowAll, IteratorColumnRegion, IteratorRowRegion
# from pysam.calignmentfile cimport pysam_get_flag, pysam_bam_get_qname
from pysam.libcalignmentfile cimport BAM_FPROPER_PAIR, BAM_FPAIRED, BAM_FREVERSE, BAM_FMREVERSE, BAM_FREAD1, BAM_FUNMAP, BAM_FMUNMAP, BAM_FDUP, pysam_bam_get_qname
from pysam.libcalignedsegment cimport PileupColumn, pysam_bam_get_seq
from pysam.libchtslib cimport bam1_t, bam_pileup1_t

from genomeview.utilities import match_chrom_format


cdef char* bam_nt16_rev_table = "=ACMGRSVTWYHKDBN"

cdef inline object get_seq_base(bam1_t *src, uint32_t k):
    cdef uint8_t* p
    cdef char* s

    if not src.core.l_qseq:
        return None

    seq = PyBytes_FromStringAndSize(NULL, 1)
    s   = <char*>seq
    p   = pysam_bam_get_seq(src)

    s[0] = bam_nt16_rev_table[p[k//2] >> 4 * (1 - k%2) & 0xf]

    return seq


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
        cdef:
            IteratorColumnRegion pileup
            PileupColumn column
            bam_pileup1_t ** plp
            bam_pileup1_t * pileupRead
            bam1_t *read
            int c, n

        chrom = match_chrom_format(self.chrom, bam.references)
	
        # for pileupcolumn in bam.pileup(self.chrom, self.start, self.end, truncate=True):
        pileup = bam.pileup(chrom, self.start, self.end, truncate=True)
        for column in pileup:
            # for pileupread in pileupcolumn.pileups:
            n = column.n
            plp = column.plp

            for i in range(n):
                pileupRead = &(plp[0][i])
                read = pileupRead.b

                if pileupRead.is_refskip:
                    continue
                elif pileupRead.is_del:
                    self.add_count(column.pos, "DEL")
                else:
                    # nuc =  pileupRead.alignment.query_sequence[pileupread.query_position]
                    nuc = get_seq_base(read, pileupRead.qpos)
                    if nuc != "N":
                        self.add_count(column.pos, nuc.decode())
                if pileupRead.indel > 0:
                    self.add_count(column.pos, "INS")

    def add_count(self, position, type_):
        position -= self.start
        if type_ == "INS":
            self.insertions[position] += 1
        else:
            if type_ not in self.types_to_id:
                return
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
