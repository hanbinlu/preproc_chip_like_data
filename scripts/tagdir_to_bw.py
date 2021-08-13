import argparse
import simple_chip_utils

parser = argparse.ArgumentParser(description="Create BigWig tracks for upload")
parser.add_argument("tagdir", type=str, help="homer TagDirectory")
parser.add_argument(
    "host", type=str, default="", help="To create uploadable bigWig link"
)
parser.add_argument(
    "webdir", type=str, default="", help="Create a symbolic link to the webdir",
)
parser.add_argument(
    "--genome_id", type=str, default="", help="Genome id for making bigWig file"
)
parser.add_argument(
    "--reusebw", action="store_false", help="Whether to create bigWig"
)
args = parser.parse_args()

if args.tagdir.endswith("/"):
    tagdir = args.tagdir[0:-1]
else:
    tagdir = args.tagdir

if not args.reusebw:
    simple_chip_utils.makeBW(tagdir, args.genome_id)

bw_path = f"{tagdir}/{tagdir}.ucsc.bigWig"
simple_chip_utils.create_bw_track_controller(
    bw_path, args.webdir, args.host,
)

