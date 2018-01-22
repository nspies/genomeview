import genomeview

def test_bed():
    file_paths = ["genes.sorted.bed.gz"]
    
    doc = genomeview.visualize_data(file_paths, "chr3", 172277030, 180005230)
    genomeview.save(doc, "bed_view.svg")