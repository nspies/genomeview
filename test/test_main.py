import pytest

import genomeview



def test_basic(bam_doc):
    with open("results/output.svg", "w") as out_svg_file:
        genomeview.render_to_file(bam_doc, out_svg_file)

    import os
    assert os.path.exists("results/output.svg")

def test_save_to_svg(bam_doc):
    genomeview.save(bam_doc, "results/temp.svg")

def test_export_to_pdf(bam_doc):
    genomeview.save(bam_doc, "results/temp.pdf")

def test_export_to_png(bam_doc):
    genomeview.save(bam_doc, "results/temp.png")


def test_arrows(reference_path):
    for i in [100, 1000, 2000, 5000]:
        print(i)
        doc = genomeview.visualize_data(["data/illumina.bam"], "chr4", 96549060, 96549060+i, reference_path)
        genomeview.save(doc, "results/temp_{}.png".format(i))


def test_view_without_source():
    import genomeview

    doc = genomeview.Document(900)
    
    view = genomeview.GenomeView("chr4", 96549060, 96549060+1000, "+")
    doc.add_view(view)

    bam_track_hg002 = genomeview.SingleEndBAMTrack("data/quick_consensus_test.bam", name="HG002")
    bam_track_hg002.draw_mismatches = False
    view.add_track(bam_track_hg002)

    axis_track = genomeview.Axis()
    view.add_track(axis_track)

    genomeview.save(doc, "results/temp_without_source.svg")


    with pytest.raises(AssertionError):
        bam_track_hg002.draw_mismatches = True
        genomeview.save(doc, "results/temp_without_source_error.svg")
