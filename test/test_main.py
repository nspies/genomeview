import genomeview



def test_basic(bam_doc):
    with open("output.svg", "w") as out_svg_file:
        genomeview.render_to_file(bam_doc, out_svg_file)

    import os
    assert os.path.exists("output.svg")


def test_export_to_pdf(bam_doc):
    genomeview.utilities.save(bam_doc, "temp.pdf")


def test_export_to_png(bam_doc):
    genomeview.utilities.save(bam_doc, "temp.png")