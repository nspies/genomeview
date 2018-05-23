import genomeview

dataset_paths = ["data/pacbio.chr1.bam",
                 "data/illumina.chr1.bam",
                 "/Users/nspies/Downloads/hg19.refseq.sorted.bed.gz"]
reference = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/reference/phase2_reference_assembly_sequence/hs37d5.fa.gz"

chrom = "chr1"
start = 224368899
end =   224398899

doc = genomeview.visualize_data(dataset_paths, chrom, start, end, reference)

genomeview.save(doc, "example.svg")

# import genomeview.track

# chrom = "14"
# start = 66901400

# genome_path = "data/chr14.fa"
        
# doc = genomeview.Document(950)
# source = genomeview.FastaGenomeSource(genome_path)

# gv = genomeview.genomeview.GenomeView("bam", chrom, start, start+10000, "+", source)

# # Add the coordinate axis at the top
# axis = genomeview.axis.Axis("axis")
# gv.add_track(axis)

# bam_track = genomeview.SingleEndBAMTrack("v1", "data/pacbio.chr14.bam")
# bam_track.quick_consensus = True
# bam_track.min_indel_size = 5
# gv.add_track(bam_track)

# # bam_track = genomeview.SingleEndBAMTrack("v2", "data/pacbio.chr14.bam")
# # bam_track.quick_consensus = False
# # gv.add_track(bam_track)

# doc.elements.append(gv)

# genomeview.render_to_file(doc, open("example.svg", "w"))