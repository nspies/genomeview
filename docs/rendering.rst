Rendering shapes and text
=========================

Drawing shapes and text
-----------------------

Each of the functions below takes as arguments information about the screen coordinates, and yields a series of SVG tags specifying lines, shapes and text to be drawn. Each function also accepts optional ``kwdargs`` which can include additional SVG attributes such as ``fill`` and ``stroke`` colors.

.. autoclass:: genomeview.svg.Renderer

   .. method:: text(self, x, y, text, size=10, anchor="middle", family="Helvetica", **kwdargs)

      Draws text. Anchor specifies the horizontal positioning of the text with respect
      to the point (x,y) and must be one of ``{start, middle, end}``. Font ``size`` and ``family`` can also be specified.

   .. method:: text_with_background(self, x, y, text, size=10, anchor="middle", family="Helvetica", text_color="black", bg="white", bg_opacity=0.8, **kwdargs)

      Draws text on an opaque background. ``bg`` specifies the background color, and ``bg_opacity`` ranges from 0 (completely transparent) to 1 (completely opaque).


   .. method:: rect(x, y, width, height, **kwdargs)

      Draws a rect whose upper left point is (x,y) with the specified 
      width and height.


   .. method:: line(x1, y1, x2, y2, **kwdargs)

      Draws a line from (x1,y1) to (x2,y2).


   .. method:: line_with_arrows(x1, y1, x2, y2, n=5, direction="right", color="black", **kwdargs)

      Draws a line from (x1,y1) to (x2,y2) with ``n`` arrows spaced between. The line and arrows will be drawn in the specified ``color``.


Converting genomic coordinates to screen coordinates
----------------------------------------------------

.. autoclass:: genomeview.Scale
   :members:
   :undoc-members: 