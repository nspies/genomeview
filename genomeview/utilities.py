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


def render_to_file(doc, outf):
    """
    Renders the document to a file-like object.
    """
    for l in doc.render():
        outf.write(l + "\n")