import pytest

import genomeview



def test_basic(bam_doc):
    with open("output.svg", "w") as out_svg_file:
        genomeview.render_to_file(bam_doc, out_svg_file)

    import os
    assert os.path.exists("output.svg")

def test_save_to_svg(bam_doc):
    genomeview.save(bam_doc, "temp.svg")

def test_export_to_pdf(bam_doc):
    genomeview.save(bam_doc, "temp.pdf")

def test_export_to_png(bam_doc):
    genomeview.save(bam_doc, "temp.png")


def test_view_without_source():
    import genomeview

    doc = genomeview.Document(900)
    
    view = genomeview.GenomeView("locus 1", "chr4", 96549060, 96549060+1000, "+")
    doc.add_view(view)

    bam_track_hg002 = genomeview.SingleEndBAMTrack("HG002", "quick_consensus_test.bam")
    bam_track_hg002.draw_mismatches = False
    view.add_track(bam_track_hg002)

    axis_track = genomeview.Axis("axis")
    view.add_track(axis_track)

    genomeview.save(doc, "temp_without_source.svg")


    with pytest.raises(AssertionError):
        bam_track_hg002.draw_mismatches = True
        genomeview.save(doc, "temp_without_source.svg")
