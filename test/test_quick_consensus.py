import pysam
from genomeview import MismatchCounts


def test_quick_consensus():
    bam = pysam.AlignmentFile("data/quick_consensus_test.bam")

    consensus = MismatchCounts("4", 96549060, 96567077)

    consensus.tally_reads(bam)


def test_compare_quick_consensus():
    from genomeview import quickconsensus
    from genomeview import _quickconsensus

    bam = pysam.AlignmentFile("data/quick_consensus_test.bam")

    cython_consensus = _quickconsensus.MismatchCounts("4", 96549060, 96549060+1000)
    python_consensus = quickconsensus.MismatchCounts("4", 96549060, 96549060+1000)

    python_consensus.tally_reads(bam)
    cython_consensus.tally_reads(bam)

    assert (cython_consensus.counts == python_consensus.counts).all()
    assert (cython_consensus.insertions == python_consensus.insertions).all()

