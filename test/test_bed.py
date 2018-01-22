import genomeview

def test_bed():
    file_paths = ["data/genes.sorted.bed.gz"]

    doc = genomeview.visualize_data(file_paths, "chr3", 179500230, 179800230)
    genomeview.save(doc, "results/bed_view.svg")