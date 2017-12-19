GenomeView Tutorial
===================
.. contents:: :local:

GenomeView is a python-based system for visualizing genomic data.

Step 1: creating the document
-----------------------------

First we'll need a document. The only argument is to define the width of the view (think of this as its pixel width)::
    
    doc = genomeview.Document(900)

The document is where all the genome views will end up.


Step 2: creating the genome views
---------------------------------

We're starting to get into the action here -- a genome view defines a set of coordinates to visualize, and allows the addition of a number of tracks displaying different types of data for those coordinates.

To create a genome view, you'll first create a genome "source" (basically a link to the reference genome sequence), then derive a view with the coordinates you'd like to visualize::
    
    source = genomeview.FastaGenomeSource("/path/to/hg19.fasta")
    view = genomeview.GenomeView("locus 1", "chr1", 219158937, 219169063, "+", source)
    doc.add_view(view)

Note that all views and tracks take as their first argument a label which must be unique within the containing document or view.

You can add as many genome views as you'd like to a single document, allowing you to visualize multiple genomic loci in the same document.


Step 3: adding the tracks to the genome view
--------------------------------------------

The next step is to create tracks visualizing the actual data and add them to the genome view. Tracks are visualized in the order that they're added, so if you'd like to put the axis at the top, add it first, and if you'd like it at the bottom, add it last.

For example::

    bam_track_hg002 = genomeview.SingleEndBAMTrack("HG002", "/path/to/hg002.sorted.bam")
    view.add_track(bam_track_hg002)

    axis_track = genomeview.Axis("axis")
    view.add_track(axis_track)


Step 4: rendering the document
------------------------------

Documents are rendered into SVG format, a standard text-based format used to display graphical objects on the web.

If you are using jupyter notebook or jupyterlab, documents can be displayed simply by placing the name of the document on the last line of a cell by itself and running the cell.

To render the document to file, use the simple ``render_to_file`` command::

    with open("/path/to/output.svg", "w") as out_svg_file:
        genomeview.render_to_file(doc, out_svg_file)

The resulting SVG file can be visualized in any modern web browser or edited in most standard vector-graphics editing programs (eg Adobe Illustrator, Affinity Designer, Inkscape).