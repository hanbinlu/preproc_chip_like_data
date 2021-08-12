# preproc_chip_like_data

**Usage 1: Process SRA (ChIP) data to uploadable bigWig track**
```
sra_chip_to_bw.py SRR7902570 \
    Med1 v6.5 2018 \ # enforce to put basic dataset info: chip target, cell type, year of the publication
    /home/software/genome_index/mouse/bowtie_indexing/mm10/mm10 mm10 \ # bowtie2 mapping
    --num_cpus 35 \
    --host http://xxx.xxx.xxxx/tracks \ # host address of the server
    --webdir /var/www/html/tracks \ # create a soft link at the serving directory
    --additional_info Oct4FV_DMSO # additional information to attach to the track name
```
The pipeline streamlines the following steps: download (curl), fastq-dump, bowtie2 mapping, makeTagDirectory (homer), makeBigWig.pl (homer), generate uploadable bw config file. If paired-end data is provided, only read 1 is processed.

**Usage 2: Generate uploadable bigWig track from Homer directory**
```
tagdir_to_bw.py tagdir_path http://xxx.xxx.xxxx/tracks /var/www/html/tracks
```
