import logging
import subprocess
import sys



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