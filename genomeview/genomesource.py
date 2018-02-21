"""
Genome Sources are used to describe reference genomes, typically either on disk (eg
:class:`genomeview.genomesource.FastaGenomeSource`) or in memory 
(:class:`genomeview.genomesource.GenomeSource`).
"""

import collections

from genomeview.utilities import match_chrom_format

comp = str.maketrans('ATCGNatcgn','TAGCNtagcn')
    
def reverse_comp(st):
    """ Returns the reverse complement of a DNA sequence; non ACGT bases will be ignored. """
    return str(st)[::-1].translate(comp)



class GenomeSource(object):
    """
    An in-memory genome source.

    Attributes:
        names_to_contigs: a `collections.OrderedDict` or similar ordered mapping specifying 
            the contig/chromosome names as keys and their sequences as values.
    """
    def __init__(self, names_to_contigs, aligner_type="bwa"):
        self.names_to_contigs = collections.OrderedDict(names_to_contigs)
        self._bwa = None
        self._ssw = None
        self._blacklist = None

        self.aligner_type = aligner_type

    def get_seq(self, chrom, start, end, strand):
        chrom = match_chrom_format(chrom, self.keys())
        seq = self.names_to_contigs[chrom][start:end+1]
        if strand == "-":
            seq = reverse_comp(seq)
        return seq

    def keys(self):
        return list(self.names_to_contigs.keys())



class FastaGenomeSource(GenomeSource):
    """ 
    A genome source based on a Fasta file. 

    This is essentially a pickle-able wrapper for pysam.FastaFile; 
    as such, it is capable of using indexed fasta files available
    via http/ftp/s3/etc.
    """
    def __init__(self, path):
        self.path = path
        self._fasta = None
        
    def get_seq(self, chrom, start, end, strand):
        chrom = match_chrom_format(chrom, self.keys())
        
        # seq = self.fasta[chrom][start:end+1]
        seq = self.fasta.fetch(chrom, start, end+1)
        if strand == "-":
            seq = reverse_comp(seq)
        return seq

    def keys(self):
        return list(self.fasta.references)

    @property
    def fasta(self):
        if self._fasta is None:
            # import pyfaidx
            # self._fasta = pyfaidx.Fasta(self.path, as_raw=True)
            import pysam
            self._fasta = pysam.FastaFile(self.path)
        return self._fasta

    def __getstate__(self):
        state = self.__dict__.copy()
        state["_fasta"] = None
        return state
