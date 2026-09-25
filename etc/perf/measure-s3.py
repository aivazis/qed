#!/usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved

# externals
import argparse
import datetime
import os
import shutil
import socket
import subprocess
import sys
import tarfile

# support
import pyre

# the measurement program
DESCRIPTION = """
Measure tile generation from a NISAR product in an S3 bucket: the cost of a tile at every zoom
level the client requests, and the throughput of the server as a function of its team size.
Everything lands in a fresh directory that is packed into a tarball at the end. The run takes a
while, so start it with nohup or inside tmux, rather than in a terminal that may go away
"""


class MeasurementError(Exception):
    """
    The base class of the reasons a measurement cannot proceed
    """


class PreflightError(MeasurementError):
    """
    The environment cannot support the measurement
    """


class ProductError(MeasurementError):
    """
    The product does not have what the measurement asked for
    """


class Log:
    """
    Echo everything to the terminal and keep a copy in the run log
    """

    def __init__(self, *, path: pyre.primitives.path, **kwds) -> None:
        # chain up
        super().__init__(**kwds)
        # open the log
        self._stream = open(path, mode="a", buffering=1)
        # all done
        return

    def say(self, message: str) -> None:
        """
        Report {message}, stamped with the time
        """
        # stamp it
        line = f"measure-s3: {datetime.datetime.now(datetime.timezone.utc):%H:%M:%S} {message}"
        # show it
        print(line, flush=True)
        # and keep it
        self._stream.write(line + "\n")
        # all done
        return

    def echo(self, line: str) -> None:
        """
        Pass along a {line} of output from somebody else
        """
        # show it
        print(line, end="", flush=True)
        # and keep it
        self._stream.write(line)
        # all done
        return

    def close(self) -> None:
        """
        Done with the log
        """
        # close the stream
        self._stream.close()
        # all done
        return


def parse() -> argparse.Namespace:
    """
    Read the command line
    """
    # make a parser
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    # the product
    parser.add_argument("uri", help="the s3 uri of the product")
    # the reader that understands it
    parser.add_argument(
        "--flavor",
        default="gslc",
        help="the nisar reader: gslc, rslc, gcov, gunw, runw, rifg; the default is gslc",
    )
    # the dataset
    parser.add_argument(
        "--dataset",
        default=None,
        help="the dataset to measure, e.g. L.A.HH; the default is the largest one",
    )
    # the channel
    parser.add_argument(
        "--channel",
        default=None,
        help="the channel to render; the default is amplitude, or the first one there is",
    )
    # the team sizes
    parser.add_argument(
        "--teams",
        default="1,2,4,8,16",
        help="the team sizes to sweep, capped by the number of cores; the default is 1,2,4,8,16",
    )
    # the repetitions
    parser.add_argument(
        "--reps", type=int, default=3, help="the repetitions of each tile measurement"
    )
    # the zoom levels
    parser.add_argument(
        "--maxzoom",
        type=int,
        default=6,
        help="the deepest decimation to measure; the default is 6, the deepest the client asks for",
    )
    # the concurrency levels
    parser.add_argument(
        "--clients",
        default="1,2,4,8,16,32",
        help="the concurrency levels of the swarms; the default is 1,2,4,8,16,32",
    )
    # the workload
    parser.add_argument(
        "--tiles", type=int, default=32, help="the tiles each concurrency level fetches"
    )
    # the port
    parser.add_argument(
        "--port", type=int, default=8181, help="the port of the servers the swarms launch"
    )
    # the results
    parser.add_argument(
        "--out",
        default=None,
        help="the directory that collects the results; the default is named after host and time",
    )
    # parse and hand off
    return parser.parse_args()


def preflight(*, uri: str, port: int, out: pyre.primitives.path) -> None:
    """
    Make sure the environment can support the measurement before anything is spent on it
    """
    # a product that is not in a bucket is a mistake
    if not uri.startswith("s3://"):
        # so say so
        raise PreflightError(f"'{uri}' is not an s3 uri")
    # so is a results directory that already exists, since the records would mix
    if out.exists():
        # so say so
        raise PreflightError(f"'{out}' already exists")
    # the installed qed must be on the path
    if shutil.which("qed") is None:
        # or there is nothing to measure with
        raise PreflightError("there is no 'qed' on the path")
    # and it must know how to aim at the data and leave the pyramid alone
    help = subprocess.run(
        ["qed", "--shell=script", "measure", "--help"], capture_output=True, text=True
    )
    # which its help says
    if "--levels" not in help.stdout + help.stderr:
        # or else it is too old
        raise PreflightError("the installed qed predates the S3 measurement options; update it")
    # the swarms need their port to themselves
    try:
        # so try to claim it
        socket.create_server(("127.0.0.1", port)).close()
    # if somebody else has it
    except OSError as error:
        # say so
        raise PreflightError(f"port {port} is taken; pick another with --port") from error
    # all done
    return


def configure(*, out: pyre.primitives.path, uri: str, flavor: str) -> None:
    """
    Write the configuration every measurement reads: the product, and nothing else, since the
    credentials come from the standard AWS chain of the instance
    """
    # the settings
    settings = (
        "# -*- yaml -*-\n"
        "\n"
        "# the product under measurement\n"
        "product:\n"
        f"    uri: {uri}\n"
        "\n"
        "# register it\n"
        "datasets:\n"
        f"    - nisar.{flavor}#product\n"
    )
    # write them
    with open(out / "qed.yaml", mode="w") as stream:
        # all at once
        stream.write(settings)
    # all done
    return


def survey(*, uri: str, flavor: str) -> list:
    """
    Open the product and list its datasets as (name, shape, tile, channels), which also checks
    that it can be reached at all
    """
    # the package, from the installation
    import qed

    # build the reader the way the configuration does
    reader = getattr(qed.readers.nisar, flavor)(name="product", uri=uri)
    # make first contact, without the statistics
    reader.open(measure=False)
    # describe each dataset
    found = [
        (
            dataset.pyre_name,
            tuple(dataset.shape),
            tuple(dataset.tile),
            tuple(dataset.channels.keys()),
        )
        for dataset in reader.datasets
    ]
    # let go of the product, so its handles close before the measurements start
    del reader
    # hand off the description
    return found


def pick(*, datasets: list, dataset: str | None, channel: str | None) -> tuple:
    """
    Choose the dataset and channel to measure: the ones named, or else the largest dataset,
    preferring one with an amplitude channel, and its amplitude or its first channel
    """
    # if a dataset was named
    if dataset is not None:
        # find it
        chosen = [entry for entry in datasets if entry[0] == f"product.{dataset}"]
        # a dataset the product does not have is a mistake
        if not chosen:
            # so say so
            raise ProductError(f"the product has no dataset '{dataset}'")
        # otherwise, it is the one
        name, shape, tile, channels = chosen[0]
    # otherwise
    else:
        # rank the datasets: amplitude first, then size
        name, shape, tile, channels = max(
            datasets, key=lambda entry: ("amplitude" in entry[3], entry[1][0] * entry[1][1])
        )
    # if a channel was named
    if channel is not None:
        # a channel the dataset does not have is a mistake
        if channel not in channels:
            # so say so
            raise ProductError(f"'{name}' has no channel '{channel}'; it has {channels}")
    # otherwise
    else:
        # amplitude if there is one, else the first
        channel = "amplitude" if "amplitude" in channels else channels[0]
    # hand off the choice
    return name, channel


def measure(*, log: Log, out: pyre.primitives.path, label: str, args: list, failures: list) -> None:
    """
    Run one measurement from {out}, noting a failure instead of abandoning the ones to come
    """
    # say what is starting
    log.say(label)
    # launch the panel from the results directory, so every process reads its configuration
    process = subprocess.Popen(
        ["qed", "--shell=script", "measure", *args],
        cwd=out,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    # pass its output along as it arrives
    for line in process.stdout:
        # to the terminal and the log
        log.echo(line)
    # wait for it to finish
    status = process.wait()
    # if it failed
    if status != 0:
        # say so
        log.say(f"{label} failed with status {status}")
        # and remember it for the summary
        failures.append(label)
    # all done
    return


def pack(*, out: pyre.primitives.path) -> pyre.primitives.path:
    """
    Pack the results directory into a tarball next to it
    """
    # the tarball
    tarball = out.parent / f"{out.name}.tar.gz"
    # make it
    with tarfile.open(tarball, mode="w:gz") as archive:
        # with the whole directory, under its own name
        archive.add(out, arcname=out.name)
    # hand it off
    return tarball


def main() -> int:
    """
    Run the whole program
    """
    # read the command line
    options = parse()
    # the number of cores, which caps the team sizes
    cores = os.cpu_count()
    # the team sizes the machine can staff
    teams = [size for size in map(int, options.teams.split(",")) if size <= cores]
    # the name of the results directory
    stamp = (
        f"qed-measure-{socket.gethostname().split('.')[0]}-{datetime.datetime.now():%Y%m%d-%H%M%S}"
    )
    # and its location
    out = pyre.primitives.path(options.out or stamp).resolve()
    # check the environment
    try:
        # before anything is spent
        preflight(uri=options.uri, port=options.port, out=out)
    # if it cannot support the measurement
    except PreflightError as error:
        # say why
        print(f"measure-s3: {error}", file=sys.stderr)
        # and bail
        return 1

    # make the results directory
    out.mkdir(parents=True)
    # and the log
    log = Log(path=out / "run.log")
    # say what is about to happen
    log.say(f"on {socket.gethostname()}, {cores} cores")
    log.say(f"product {options.uri} as nisar.{options.flavor}")
    log.say(f"results in {out}")

    # record the installation, so the numbers can be tied to the code that produced them
    about = subprocess.run(
        ["qed", "--shell=script", "about"], cwd=out, capture_output=True, text=True
    )
    # keep it
    with open(out / "about.txt", mode="w") as stream:
        # all of it
        stream.write(about.stdout + about.stderr)
    # and show it
    log.echo(about.stdout + about.stderr)

    # write the configuration
    configure(out=out, uri=options.uri, flavor=options.flavor)
    # find out what the product holds
    try:
        # open it
        datasets = survey(uri=options.uri, flavor=options.flavor)
        # and choose what to measure
        dataset, channel = pick(datasets=datasets, dataset=options.dataset, channel=options.channel)
    # if the product lacks what was asked for
    except ProductError as error:
        # say why
        log.say(str(error))
        # and bail
        return 1
    # keep the description of the product
    with open(out / "product.txt", mode="w") as stream:
        # one dataset per line
        for name, shape, tile, channels in datasets:
            # with its shape, its tile, and its channels
            stream.write(f"{name} {shape[0]}x{shape[1]} {tile[0]}x{tile[1]} {','.join(channels)}\n")
    # show it
    with open(out / "product.txt", mode="r") as stream:
        # all of it
        log.echo(stream.read())
    # say what will be measured
    log.say(f"measuring {dataset}, channel {channel}")

    # the restrictions every measurement shares
    target = ["--only=product", f"--rasters={dataset}", f"--channels={channel}"]
    # the measurements that did not complete
    failures = []

    # the zoom levels: a 512 tile, the one the client asks for, at every decimation the client
    # requests, each point in a fresh process so nothing is served from a cache
    for rep in range(1, options.reps + 1):
        # measure
        measure(
            log=log,
            out=out,
            label=f"zoom ladder, pass {rep} of {options.reps}",
            args=[
                "tile",
                *target,
                "--shapes=9,10",
                f"--zooms=0,{options.maxzoom + 1}",
                "--cold=yes",
                "--sample=no",
                f"--output={out / 'tiles.csv'}",
            ],
            failures=failures,
        )

    # the tile sizes: 256 through 2048 at full resolution, which separates the fixed cost of a
    # request from the cost of each pixel
    for rep in range(1, options.reps + 1):
        # measure
        measure(
            log=log,
            out=out,
            label=f"shape ladder, pass {rep} of {options.reps}",
            args=[
                "tile",
                *target,
                "--shapes=8,12",
                "--zooms=0,1",
                "--cold=yes",
                "--sample=no",
                f"--output={out / 'tiles.csv'}",
            ],
            failures=failures,
        )

    # fit the cost model to everything the ladders recorded
    measure(
        log=log,
        out=out,
        label="fit",
        args=["fit", f"--output={out / 'tiles.csv'}"],
        failures=failures,
    )

    # the team sizes: a server per size, full resolution tiles of 512, every concurrency level
    # served tiles nobody has fetched, and no pyramid, so every tile is read from the bucket
    for team in teams:
        # measure
        measure(
            log=log,
            out=out,
            label=f"swarm with a team of {team}",
            args=[
                "swarm",
                *target,
                "--shapes=9,10",
                "--zooms=0,1",
                f"--team={team}",
                f"--clients={options.clients}",
                f"--tiles={options.tiles}",
                "--warm=no",
                "--levels=no",
                "--sample=no",
                f"--port={options.port}",
                f"--output={out / f'swarm-team{team}.csv'}",
            ],
            failures=failures,
        )

    # say it is over
    log.say("done")
    # and list whatever did not complete, so a partial result is never mistaken for a whole
    for label in failures:
        # one per line
        log.say(f"incomplete: {label}")
    # close the log, so it is whole in the tarball
    log.close()
    # pack the results
    tarball = pack(out=out)
    # and say where they are
    print(f"measure-s3: results packed in {tarball}", flush=True)
    # report failures through the exit status too
    return 1 if failures else 0


# entry point
if __name__ == "__main__":
    # run the program and report its status
    sys.exit(main())


# end of file
