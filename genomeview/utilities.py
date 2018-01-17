import os
import tempfile

from genomeview.export import convert_svg


def match_chrom_format(chrom, keys):
    if chrom in keys:
        return chrom
    if "chr" in chrom:
        chrom2 = chrom.replace("chr", "")
    else:
        chrom2 = "chr{}".format(chrom)
        
    if chrom2 in keys:
        return chrom2
    return chrom



def save(doc, outpath, outformat=None):
    if isinstance(outpath, bytes):
        outpath = outpath.decode()

    if outformat is None:
        if outpath.endswith(".pdf"):
            outformat = "pdf"
        elif outpath.endswith(".png"):
            outformat = "png"

    if outformat == "svg":
        with open(outpath, "w") as outf:
            render_to_file(doc, outf)
    else:
        with tempfile.TemporaryDirectory() as outdir:
            temp_svg_path = os.path.join(outdir, "temp.svg")
            with open(temp_svg_path, "w") as outf:
                render_to_file(doc, outf)

            convert_svg(temp_svg_path, outpath, outformat)



def render_to_file(doc, outf):
    """
    Renders the document as an svg to a file-like object.
    """

    for l in doc.render():
        outf.write(l + "\n")