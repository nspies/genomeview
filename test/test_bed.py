import genomeview

def test_bed():
    file_paths = ["/Users/nspies/Downloads/hg19.refseq.sorted.bed.gz"]
    doc = genomeview.visualize_data(file_paths, "chr3", 178780124, 179038684)
    genomeview.save(doc, "bed_view.svg")