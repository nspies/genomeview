import collections
import os

import genomeview
from genomeview import utilities


def visualize_data(file_paths, chrom, start, end, reference_path=None, 
                   width=900, axis_on_top=False):
    """
    Creates a GenomeView document to display the data in the specified
    files (eg bam, bed, etc).

    Args:
        file_paths: this specifies the file paths to be rendered. It must be 
            either a list/tuple of the paths, or a dictionary mapping 
            {track_name:path}. (If you are using a python version prior to 3.6, 
            use collections.ordereddict to ensure the order remains the same.)
            Currently supports files ending in .bam, .cram, .bed, .bed.gz, 
            .bigbed, or .bigwig (or .bw). Most of these file types require a
            separate index file to be present (eg a .bam.bai or a .bed.gz.tbi 
            file must exist).
        chrom: chromosome (or contig) to be rendered
        start: start coordinate of region to be rendered
        end: end coordinate of region to be rendered
        reference_path: path to fasta file specifying reference genomic 
            sequence. This is required in order to display mismatches
            in bam tracks.
        width: the pixel width of the document
        axis_on_top: specifies whether the axis should be added at the bottom
            (default) or at the top
    """
    if reference_path is not None:
        source = genomeview.FastaGenomeSource(reference_path)
    else:
        source = None

    doc = genomeview.Document(width)
    
    view = genomeview.GenomeView(chrom, start, end, "+", source)
    doc.add_view(view)

    def add_axis():
        axis_track = genomeview.Axis("axis")
        view.add_track(axis_track)

    if axis_on_top:
        add_axis()

    if isinstance(file_paths, collections.Mapping):
        names = file_paths.keys()
        file_paths = [file_paths[name] for name in names]
    else:
        names = [None] * len(file_paths)
        file_paths = file_paths
        
    for name, path in zip(names, file_paths):
        if path.lower().endswith(".bam") or path.lower().endswith(".cram"):
            if utilities.is_paired_end(path):
                cur_track = genomeview.PairedEndBAMTrack(path, name=name)
            else:
                cur_track = genomeview.SingleEndBAMTrack(path, name=name)
                if utilities.is_long_frag_dataset(path):
                    cur_track.min_indel_size = 5

        elif path.lower().endswith(".bed") or path.lower().endswith(".bed.gz") or path.lower().endswith(".bigbed"):
            cur_track = genomeview.BEDTrack(path, name=name)

        elif path.lower().endswith(".bigwig") or path.lower().endswith(".bw"):
            cur_track = genomeview.BigWigTrack(path, name=name)

        else:
            suffix =  os.path.basename(path)
            raise ValueError("Unknown file suffix: {}".format(suffix))

        view.add_track(cur_track)

    if not axis_on_top:
        add_axis()

    return doc
