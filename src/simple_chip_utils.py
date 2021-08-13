import subprocess, logging, os, random

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s: %(message)s")
log_stream = logging.StreamHandler()
log_stream.setLevel(logging.INFO)
log_stream.setFormatter(formatter)
logger.addHandler(log_stream)


def dump_srr(accession, paired=True, url="", sra_dump_tool="fastq-dump"):
    if not url:
        url = f"https://sra-pub-run-odp.s3.amazonaws.com/sra/{accession}/{accession}"

    # download SRR
    download = subprocess.run(["curl", "-O", url], capture_output=True)
    if download.returncode != 0:
        raise ConnectionError(download.stderr.decode())

    # dump
    if paired:
        dump = subprocess.run(
            [sra_dump_tool, "--gzip", "--split-files", f"./{accession}"],
            capture_output=True,
        )
    else:
        dump = subprocess.run(
            [sra_dump_tool, "--gzip", f"./{accession}"], capture_output=True
        )

    if dump.returncode != 0:
        raise ConnectionError(dump.stderr.decode())

    for line in dump.stdout.decode().split("\n"):
        logger.info(line)

    base_acc = url.split("/")[-1]
    if paired:
        return f"{base_acc}_1.fastq.gz", base_acc
    else:
        return f"{base_acc}.fastq.gz", base_acc


def single_end_bowtie2_mapping(
    fq, genome_index, num_cpus, out, bowtie_opts=None, bowtie2_path="bowtie2"
):
    with open(out, "wb") as o:
        mapping = subprocess.Popen(
            [bowtie2_path, "-x", genome_index, "-p", str(num_cpus), fq],
            stdout=o,
            stderr=subprocess.PIPE,
        )

        for line in iter(mapping.stderr.readline, b""):
            logger.info(line.decode().rstrip())

        mapping.wait()


###############################
# homer workflow
###############################
def makeTagDirectory(sam, out):
    with open(f"{out}.mktd.log", "wb") as o:
        mktd = subprocess.run(
            ["makeTagDirectory", out, sam, "-tbp", "1"], stderr=o
        )

    subprocess.run(["mv", f"{out}.mktd.log", out])


def makeBW(tgdir, genome_id):
    subprocess.run(
        [
            "makeBigWig.pl",
            tgdir,
            genome_id,
            "-url",
            "NA",
            "-webdir",
            "NA",
            "-update",
        ],
        stderr=subprocess.DEVNULL,
    )


def create_bw_track_controller(
    bw_path, webdir, host, track_name=None, color=None
):
    if track_name is None:
        track_name = bw_path.split("/")[-1]

    if color is None:
        color = f"{random.randrange(0, 256)},{random.randrange(0, 256)},{random.randrange(0, 256)}"

    # host url for the webdir
    subprocess.run(
        ["ln", "-s", os.path.abspath(bw_path), os.path.abspath(webdir)]
    )
    track_ctl = (
        "track type=bigWig "
        + f"name={track_name} "
        + f"bigDataUrl={host}/{track_name} "
        + f"color={color} "
        + 'visibility=full yLineOnOff=on autoScale=on yLineMark="0.0" alwaysZero=on graphType=bar maxHeightPixels=128:75:11 windowingFunction=maximum smoothingWindow=off'
    )

    with open(f"{bw_path}.track_control.txt", "w") as o:
        o.write(track_ctl)

    bw = bw_path.split("/")[-1]
    with open(f"{webdir}/{bw}.track_control.txt", "w") as o:
        o.write(
            "#"
            + " ".join(
                ["ln", "-s", os.path.abspath(bw_path), os.path.abspath(webdir)]
            )
            + "\n"
        )
        o.write(track_ctl)
