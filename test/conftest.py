import pytest
import os


def pytest_configure(config):
    os.chdir(os.path.dirname(__file__))

    os.makedirs("results", exist_ok=True)

@pytest.fixture
def reference_path():
    # download chr4 from ucsc if needed
    reference_path = "data/chr4.fa"

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
    
    view = genomeview.GenomeView("chr4", 96549060, 96549060+250, "+", source)
    doc.add_view(view)

    bam_track_hg002 = genomeview.SingleEndBAMTrack("data/quick_consensus_test.bam", name="HG002")
    bam_track_hg002.min_indel_size = 3
    view.add_track(bam_track_hg002)

    axis_track = genomeview.Axis()
    view.add_track(axis_track)

    return doc