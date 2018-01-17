import pytest
import os

@pytest.fixture
def reference_path():
    # download chr4 from ucsc if needed
    reference_path = "chr4.fa"

    if not os.path.exists(reference_path):
        import urllib.request
        import zlib
        url = "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/chromosomes/chr4.fa.gz"

        resource = urllib.request.urlopen(url)

        with open(reference_path, "w") as outf:
            data = zlib.decompress(resource.read(), 16+zlib.MAX_WBITS).decode("utf-8")
            outf.write(data)

    return reference_path

@pytest.fixture
def bam_doc():
    import genomeview
    source = genomeview.FastaGenomeSource(reference_path())

    doc = genomeview.Document(900)
    
    view = genomeview.GenomeView("locus 1", "chr4", 96549060, 96549060+1000, "+", source)
    doc.add_view(view)

    bam_track_hg002 = genomeview.SingleEndBAMTrack("HG002", "quick_consensus_test.bam")
    view.add_track(bam_track_hg002)

    axis_track = genomeview.Axis("axis")
    view.add_track(axis_track)

    return doc