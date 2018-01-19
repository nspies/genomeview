import os

import genomeview
from genomeview import utilities


def visualize_data(file_paths, chrom, start, end, reference_path=None, width=900, axis_on_top=False):
    if reference_path is not None:
        source = genomeview.FastaGenomeSource(reference_path)
    else:
        source = None

    doc = genomeview.Document(width)
    
    view = genomeview.GenomeView("view", chrom, start, end, "+", source)
    doc.add_view(view)

    def add_axis():
        axis_track = genomeview.Axis("axis")
        view.add_track(axis_track)

    if axis_on_top:
        add_axis()

    for i, path in enumerate(file_paths):
        path = path.lower()

        if path.endswith(".bam") or path.endswith(".cram"):
            if utilities.is_paired_end:
                name = "BAM{}".format(i)
                cur_track = genomeview.PairedEndBAMTrack(name, path)
            else:
                name = "BAM{}".format(i)
                cur_track = genomeview.SingleEndBAMTrack(name, path)
        elif path.endswith(".bed") or path.endswith(".bed.gz"):
            name = "BED{}".format(i)
            cur_track = genomeview.BEDTrack(name, path)

        else:
            suffix =  os.path.basename(path)
            raise ValueError("Unknown file suffix: {}".format(suffix))

        view.add_track(cur_track)

    if not axis_on_top:
        add_axis()

    return doc
