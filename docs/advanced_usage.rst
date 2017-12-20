Advanced Usage
==============

GenomeView is designed to be easily extended. The source code is a good place to start, but this document gives some insights into the design philosophy and the components involved in visualizing genomic data.


Graphics model
--------------

As explained in the tutorial, GenomeView lays out visual elements by nesting documents, views and tracks together, for example::
    
    doc
    -> genomeview 1
    ----> bam track 1
    ----> bam track 2
    ----> axis
    -> genomeview 2
    ----> bam track 3
    ----> axis

Visualization is accomplished by traversing that hierarchy and asking each element to display itself as SVG code. In practice, each visual element has a ``render()`` method which yields lines of SVG code which specify the lines, shapes, text, etc used to display genomic data.

To simplify this process, an :py:class:`SVG Renderer <genomeview.svg.Renderer>` object is passed along, providing a series of SVG primitive commands to enable drawing lines, shapes and text. This renderer takes care of compositing different visual elements such that x,y-coordinates can be specified relative to a local coordinate system. Shapes extending out of the region allocated for a specific visual element are clipped (eg reads extending past the last coordinate of the current window).

In addition, each :py:class:`Track <genomeview.track.Track>` maintains a :py:class:`Scale <genomeview.Scale>` object which can be used to convert genomic coordinates to screen coordinates.


Adding visual elements to existing tracks
-----------------------------------------

Each track object can include one or more pre-renderer or post-renderer functions which are used to draw items under or above the track. For example, the following post-renderer adds some text to the middle of an existing track::

   def draw_label(renderer, element):
       x_middle = element.scale.pixel_width / 2
       y_middle = element.height / 2
       yield from renderer.text_with_background(x_middle, y_middle, "hello", anchor="middle")

   track.prerenderers = [draw_label]

See the bams.ipynb jupyter notebook for more examples.


Custom tracks
-------------

While the tracks included with GenomeView contain numerous configurable options, sometimes it is necessary to either create a subclass providing new functionality.

Tracks should subclass from :py:class:`genomeview.Track` or one of its subclasses. The ``layout`` method is called once prior to rendering in order to determine the height of the element (variable height tracks allow visualizing all reads in a window even when they are stacked high). Then the ``render(self, renderer)`` method is called, taking as  argument a :py:class:`genomeview.svg.Renderer`. Note that the ``scale`` object can be accessed as ``self.scale`` in order to convert genomic coordinates to screen positions.

Renderers should use the python 3.3+ ``yield from renderer.shape()`` command to yield complex multi-line SVG shapes created by the renderer.