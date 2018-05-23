import genomeview
import pytest


def test_bed():
    file_paths = ["data/genes.sorted.bed.gz"]

    doc = genomeview.visualize_data(file_paths, "chr3", 179500230, 179800230)
    genomeview.save(doc, "results/bed_view.svg")


@pytest.mark.parametrize("which_bed", ["bed3", "bed8"])
def test_bed2(which_bed):
    file_paths = ["data/{}.bed".format(which_bed)]

    doc = genomeview.visualize_data(file_paths, "chr3", 179500230, 179800230)
    genomeview.save(doc, "results/{}_view.svg".format(which_bed))


