import pysam

def match_chrom_format(chrom, keys):
    if chrom in keys:
        return chrom
    if "chr" in chrom:
        chrom2 = chrom.replace("chr", "")
    else:
        chrom2 = "chr{}".format(chrom)
        
    if chrom2 in keys:
        return chrom2
    return chrom

def is_paired_end(bam_path, n=100):
    bam = pysam.AlignmentFile(bam_path)

    count = 0
    for read in bam.fetch():
        if read.is_paired:
            return True
        if count >= n:
            break

    return False

