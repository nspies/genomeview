import genomeview

def test_basic(reference_path):
    source = genomeview.FastaGenomeSource(reference_path)

    doc = genomeview.Document(900)
    
    view = genomeview.GenomeView("locus 1", "chr4", 96549060, 96549060+1000, "+", source)
    doc.add_view(view)

    bam_track_hg002 = genomeview.SingleEndBAMTrack("HG002", "quick_consensus_test.bam")
    view.add_track(bam_track_hg002)

    axis_track = genomeview.Axis("axis")
    view.add_track(axis_track)

    with open("output.svg", "w") as out_svg_file:
        genomeview.render_to_file(doc, out_svg_file)

    import os
    assert os.path.exists("output.svg")