import pytest
import os

@pytest.fixture
def reference_path():
    # download chr4 from ucsc if needed
    reference_path = "chr4.fa"

    if not os.path.exists(reference_path):
        import urllib.request
        import zlib
        url = "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/chromosomes/chr4.fa.gz"

        resource = urllib.request.urlopen(url)

        with open(reference_path, "w") as outf:
            data = zlib.decompress(resource.read(), 16+zlib.MAX_WBITS).decode("utf-8")
            outf.write(data)

    return reference_path