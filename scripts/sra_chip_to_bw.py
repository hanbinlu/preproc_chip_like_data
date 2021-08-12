import argparse, logging
import subprocess
import simple_chip_utils

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("Preprocess_ChIP")
formatter = logging.Formatter("%(asctime)s: %(message)s")
log_stream = logging.StreamHandler()
log_stream.setLevel(logging.INFO)
log_stream.setFormatter(formatter)
logger.addHandler(log_stream)

parser = argparse.ArgumentParser(
    description="Process published ChIP data (SRA), generate TagDirectory and BigWig track"
)
parser.add_argument("sra_acc", type=str, help="Accession for SRA data")
parser.add_argument(
    "ab", type=str, help="Antibody target (enforce information)"
)
parser.add_argument(
    "cell_type", type=str, help="Cell type of the data (enforce information)"
)
parser.add_argument(
    "year", type=str, help="Year publication (enforce information)"
)
parser.add_argument("genome_index", type=str, help="bowtie2 genome index")
parser.add_argument(
    "genome_id", type=str, help="Genome id for making bigWig file"
)

parser.add_argument(
    "--additional_info",
    type=str,
    default="",
    help="Additional information to put in the name",
)
parser.add_argument(
    "--host", type=str, default="", help="To create uploadable bigWig link"
)
parser.add_argument(
    "--webdir",
    type=str,
    default="",
    help="Create a symbolic link to the webdir",
)
parser.add_argument(
    "--paired",
    action="store_true",
    default=False,
    help="PE sequencing data, default: False",
)
parser.add_argument(
    "--url",
    type=str,
    default="",
    help="url for downloading the SRA, default generate generic SRA aws link",
)
parser.add_argument(
    "--fqdump_path",
    type=str,
    help="fastq-dump program path, default to find in env PATH",
    default="fastq-dump",
)
parser.add_argument(
    "--bowtie2_path",
    type=str,
    help="bowtie2 program path, default to find in env PATH",
    default="bowtie2",
)
parser.add_argument(
    "--num_cpus",
    type=int,
    help="number of cpu cores to use, default 8",
    default=8,
)
args = parser.parse_args()

logger.info("=========Dumping Data=========")
if args.paired:
    out_prefix = f"{args.sra_acc}_1_{args.ab}_{args.cell_type}_{args.year}"
else:
    out_prefix = f"{args.sra_acc}_{args.ab}_{args.cell_type}_{args.year}"
if args.additional_info:
    out_prefix += f"_{args.additional_info}"

fq, acc = simple_chip_utils.dump_srr(
    args.sra_acc, args.paired, args.url, args.fqdump_path
)
logger.info("=========Mapping Data=========")
simple_chip_utils.single_end_bowtie2_mapping(
    fq,
    args.genome_index,
    args.num_cpus,
    f"{out_prefix}.sam",
    bowtie2_path=args.bowtie2_path,
)
logger.info("=========MakeTagDirectory=========")
simple_chip_utils.makeTagDirectory(f"{out_prefix}.sam", f"{out_prefix}.tagdir")
logger.info("=========Making BigWig=========")
simple_chip_utils.makeBW(f"{out_prefix}.tagdir", args.genome_id)
# create bigWig url and track control
if args.host and args.webdir:
    simple_chip_utils.create_bw_track_controller(
        f"{out_prefix}.tagdir/{out_prefix}.tagdir.ucsc.bigWig",
        args.webdir,
        args.host,
    )

subprocess.run(["rm", acc, fq, f"{out_prefix}.sam"])

