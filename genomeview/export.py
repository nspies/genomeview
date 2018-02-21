import logging
import os
import subprocess
import sys
import tempfile


def save(doc, outpath, outformat=None):
    """
    Saves document `doc` to a file at `outpath`. By default, this file 
    will be in SVG format; if it ends with .pdf or .png, or if outformat
    is specified, the document will be converted to PDF or PNG if possible.

    Conversion to PDF and PNG require rsvg-convert (provided by librsvg), 
    inkscape or webkitToPDF (PDF conversion only).

    Attributes:
        doc: the :py:class:`genomeview.Document` to be saved
        outpath: a string specifying the file to save to; file extensions of
            .pdf or .png will change the default output format
        outformat: override the file format; must be one of "pdf", "png", or
            (the default) "svg"
    """
    if isinstance(outpath, bytes):
        outpath = outpath.decode()

    if outformat is None:
        if outpath.lower().endswith(".pdf"):
            outformat = "pdf"
        elif outpath.lower().endswith(".png"):
            outformat = "png"
        else:
            outformat = "svg"

    if outformat == "svg":
        with open(outpath, "w") as outf:
            render_to_file(doc, outf)
    else:
        # render to a temporary file then convert to PDF or PNG
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




#############################################################################
######################### low-level functionality ###########################
#############################################################################

        

def convert_svg(inpath, outpath, outformat):
    converter = _getExportConverter(outformat)

    if converter == "webkittopdf":
        exportData = _convertSVG_webkitToPDF(inpath, outpath, outformat)
    elif converter == "librsvg":
        exportData = _convertSVG_rsvg_convert(inpath, outpath, outformat)
    elif converter == "inkscape":
        exportData = _convertSVG_inkscape(inpath, outpath, outformat)

    return exportData


def _getExportConverter(exportFormat, requested_converter=None):
    if requested_converter == "webkittopdf" and exportFormat=="png":
        logging.error("webkitToPDF does not support export to PNG; use librsvg or inkscape instead, or "
            "export to PDF")
        sys.exit(1)

    if exportFormat == "png" and requested_converter is None:
        return "librsvg"

    if requested_converter == "rsvg-convert":
        return "librsvg"

    if requested_converter in [None, "webkittopdf"]:
        if _checkWebkitToPDF():
            return "webkittopdf"

    if requested_converter in [None, "librsvg"]:
        if _checkRSVGConvert():
            return "librsvg"

    if requested_converter in [None, "inkscape"]:
        if _checkInkscape():
            return "inkscape"

    raise Exception("No converter found for conversion to {}".format(exportFormat))
    return None



def _checkWebkitToPDF():
    try:
        subprocess.check_call("webkitToPDF", stderr=subprocess.PIPE, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def _checkRSVGConvert():
    try:
        subprocess.check_call("rsvg-convert -v", stdout=subprocess.PIPE, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def _checkInkscape():
    try:
        subprocess.check_call("inkscape --version", stdout=subprocess.PIPE, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False



def _convertSVG_webkitToPDF(inpath, outpath, outformat):
    if outformat.lower() != "pdf":
        return None

    try:
        cmd = "webkitToPDF {} {}".format(inpath, outpath)
        subprocess.check_call(cmd, shell=True)#, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return None

    return open(outpath, "rb").read()

def _convertSVG_inkscape(inpath, outpath, outformat):
    options = ""
    outformat = outformat.lower()
    if outformat == "png":
        options = "--export-dpi 150 --export-background white"

    try:
        subprocess.check_call("inkscape {} {} --export-{}={}".format(options, inpath, outformat, outpath), 
            shell=True)
    except subprocess.CalledProcessError as e:
        print("EXPORT ERROR:", str(e))

    return open(outpath, "rb").read()


def _convertSVG_rsvg_convert(inpath, outpath, outformat):
    options = ""
    outformat = outformat.lower()
    if outformat == "png":
        options = "-a --background-color white"

    try:
        subprocess.check_call("rsvg-convert -f {} {} -o {} {}".format(outformat, options, outpath, inpath), shell=True)
    except subprocess.CalledProcessError as e:
        print("EXPORT ERROR:", str(e))

    return open(outpath, "rb").read()