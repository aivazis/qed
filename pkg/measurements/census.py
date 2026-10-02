# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# externals
import collections
import csv
import gzip
import io
import itertools
import os
import statistics
import tarfile
import zlib

# support
import journal
import qed

# the measures of a raster the analyses report, as (name, label, whether lower is better)
MEASURES = (
    ("once", "bytes moved per byte stored, the raster read alone, each page fetched once", True),
    (
        "joint",
        "bytes moved per byte stored, the raster read with the rasters sharing its pages",
        True,
    ),
    ("alone", "bytes moved per byte stored, the chunks read one at a time", True),
    ("fill_mean", "share of each page the raster fills, mean", False),
    ("locality", "share of consecutive chunks on a page that are neighbors on the raster", False),
    ("empty", "share of the written chunks that are nearly empty", True),
    ("unwritten", "share of the chunk grid never written", True),
    ("compression", "compression ratio", None),
    ("stored_mib", "bytes the raster stores, in MiB", None),
    ("empty_mib", "bytes the nearly empty chunks store, in MiB", True),
    ("empty_page_share", "share of the pages that hold nothing but nearly empty chunks", True),
    ("decode_ms", "time to decode the smallest chunk, in ms", True),
    ("make_ms", "time to make the smallest chunk from its one value, in ms", None),
    ("data_decode_ms", "time to decode the median chunk of data, in ms", None),
    ("fill_mib", "bytes stored by the chunks that hold nothing but the fill, in MiB", True),
    ("fill_chunks", "chunks that hold nothing but the fill", True),
    ("encode_ms", "time to encode a chunk that holds nothing but the fill, in ms", None),
)
# the storage settings every raster records
SETTINGS = (
    "strategy",
    "page_size",
    "cell",
    "tile",
    "filters",
    "crid",
    "hdf5_fill_status",
    "hdf5_fill",
    "cf_fill",
    "smallest_holds",
    "fill_agrees",
    "deflate_level",
)
# the settings a census records only since it started looking at the fill
FILL = ("hdf5_fill_status", "hdf5_fill", "cf_fill", "smallest_holds", "deflate_level")


def load(*, source: str) -> list:
    """
    Read the summaries of a census from {source}: its {census.csv}, the folder that holds it, or
    the tarball the census packed it into
    """
    # a tarball
    if source.endswith((".tar.gz", ".tgz")):
        # is read as a stream, stopping at the summaries, which come early
        with tarfile.open(source, mode="r|gz") as archive:
            # go through its members
            for member in archive:
                # the summaries of the census sit at the top of its folder
                if member.name.count("/") == 1 and member.name.endswith("/census.csv"):
                    # read them whole, since the stream of a compressed archive cannot seek
                    text = archive.extractfile(member).read().decode("utf-8")
                    # and parse them
                    return list(csv.DictReader(io.StringIO(text)))
        # a tarball without them is a mistake
        raise FileNotFoundError(f"'{source}' holds no census.csv")
    # a folder holds its summaries in {census.csv}
    path = os.path.join(source, "census.csv") if os.path.isdir(source) else source
    # read them
    with open(path, newline="") as stream:
        # and parse them
        return list(csv.DictReader(stream))


def cycle(*, granule: str, registrar):
    """
    The repeat cycle of {granule}, as the granule id {registrar} reads it, or {None} if the id is
    not recognized; for a pair, the cycle of its reference acquisition
    """
    # the raw fields of the id
    fields = registrar.fields(granule)
    # an id the parser does not recognize
    if fields is None:
        # has no cycle
        return None
    # otherwise, the cycle, which for a pair is the one of its reference acquisition
    found = fields.get("cycle") or fields.get("referenceCycle")
    # as a number
    return int(found) if found is not None else None


def reference(*, name: str, rows: list, bins: int = 10) -> dict:
    """
    Summarize the census {name} from its {rows} as reference data for the comparison of a single
    raster against its kind: the product and cycle it covers, the summary of all its rasters, and
    one for each kind of raster, named by the last part of the raster name, e.g. {HHHH} or {mask}
    """
    # the products the census covers, and the most common one
    products = collections.Counter(row["kind"] for row in rows)
    # the parser of the granule ids
    registrar = qed.readers.nisar.daac.registrar()
    # the cycles of the granules, and the most common one
    cycles = collections.Counter(
        cycle(granule=granule, registrar=registrar) for granule in {row["granule"] for row in rows}
    )
    # the rasters by their kind
    kinds = groups(rows=rows, key=lambda row: raster(row=row).split(".")[-1])
    # assemble
    return {
        "census": name,
        "product": products.most_common(1)[0][0] if products else None,
        "cycle": cycles.most_common(1)[0][0] if cycles else None,
        "rasters": len(rows),
        "granules": len({row["granule"] for row in rows}),
        "measures": summarize(rows=rows, bins=bins),
        "groups": {
            kind: {"rasters": len(members), "measures": summarize(rows=members, bins=bins)}
            for kind, members in sorted(kinds.items())
        },
    }


def summarize(*, rows: list, bins: int = 10) -> dict:
    """
    The percentiles of every measure over {rows}, and a histogram of its values in {bins} bins of
    equal width from the smallest value to the 90th percentile, with every value past that in the
    last bin, so that a long tail does not crowd the rest into the first bin
    """
    # the measures
    measures = {}
    # go through them
    for measure, label, lower in MEASURES:
        # the values the census recorded
        numbers = values(rows=rows, name=measure)
        # without any
        if not numbers:
            # there is nothing to report
            continue
        # the percentiles
        p10, median, p90, top = percentiles(numbers=numbers)
        # the range of the histogram: from the smallest to the 90th percentile, unless that
        # leaves nothing to spread, in which case to the largest
        low = min(numbers)
        high = p90 if p90 > low else top
        # the width of a bin, with a degenerate range spread over a single unit
        width = (high - low) / bins if high > low else 1
        # count the values in each bin, keeping everything past the top edge in the last one
        counts = [0] * bins
        for number in numbers:
            # by finding its bin
            counts[min(int((number - low) / width), bins - 1)] += 1
        # record
        measures[measure] = {
            "label": label,
            "lower": lower,
            "count": len(numbers),
            "p10": p10,
            "median": median,
            "p90": p90,
            "max": top,
            "low": low,
            "high": high,
            "bins": counts,
        }
    # hand off the measures
    return measures


def measures(*, description: dict) -> dict:
    """
    The measures of a single raster, from the {description} of how it sits in its file that
    {qed.readers.pages.describe} makes, by the names the census gives them
    """
    # unpack
    record = description["record"]
    fill = description["nodata"]
    # divide, leaving out what cannot be computed
    ratio = lambda top, bottom: top / bottom if top is not None and bottom else None
    # scale, leaving out what is missing
    scale = lambda value, factor: value * factor if value is not None else None
    # the measures
    return {
        "once": record.get("once"),
        "joint": record.get("joint"),
        "alone": record.get("alone"),
        "fill_mean": record.get("fillMean"),
        "locality": record.get("locality"),
        "empty": ratio(record["empty"], record["written"]),
        "unwritten": 1 - record["written"] / record["grid"] if record["grid"] else None,
        "compression": record.get("compression"),
        "stored_mib": record["stored"] / 2**20,
        "empty_mib": record["emptyStored"] / 2**20,
        "empty_page_share": ratio(record.get("emptyPages"), record.get("pages")),
        "decode_ms": scale(fill.get("decode"), 1e3),
        "make_ms": scale(fill.get("make"), 1e3),
        "data_decode_ms": scale(fill.get("data"), 1e3),
        "fill_mib": scale(fill.get("fillBytes"), 2**-20),
        "fill_chunks": fill.get("fillChunks"),
        "encode_ms": scale(fill.get("encode"), 1e3),
    }


def chunks(*, source: str):
    """
    Generate the per chunk records of a census in {source}, its folder or the tarball it was
    packed into, as (granule, dataset, stored bytes, raw bytes)
    """
    # a tarball
    if source.endswith((".tar.gz", ".tgz")):
        # is read as a stream
        with tarfile.open(source, mode="r|gz") as archive:
            # go through its members
            for member in archive:
                # the chunk records of a granule sit in its folder
                if not member.name.endswith("/layout-pages.csv.gz"):
                    # so skip everything else
                    continue
                # the granule is the name of the folder
                granule = member.name.split("/")[-2]
                # read them whole, since the stream of a compressed archive cannot seek
                text = _decompress(granule=granule, data=archive.extractfile(member).read())
                # a file that cannot be read
                if text is None:
                    # leaves its granule out
                    continue
                # hand the rest off
                yield from _chunks(granule=granule, stream=io.StringIO(text))
        # all done
        return
    # a folder holds a folder for each product, and one for each granule in it
    for folder, _, files in sorted(os.walk(source)):
        # the ones with chunk records
        if "layout-pages.csv.gz" not in files:
            # are the only ones of interest
            continue
        # the granule is the name of the folder
        granule = os.path.basename(folder)
        # read them whole
        with open(os.path.join(folder, "layout-pages.csv.gz"), mode="rb") as stream:
            # and decompress them
            text = _decompress(granule=granule, data=stream.read())
        # a file that cannot be read
        if text is None:
            # leaves its granule out
            continue
        # hand the rest off
        yield from _chunks(granule=granule, stream=io.StringIO(text))
    # all done
    return


def _decompress(*, granule: str, data: bytes):
    """
    Decompress the chunk records of {granule} in {data}, or return {None}, with a warning, when
    they are damaged, e.g. by a measurement that was stopped while it was writing them; a partial
    table would undercount the chunks of the granule, so none of it is used
    """
    # carefully
    try:
        # decompress them
        return gzip.decompress(data).decode("utf-8")
    # if they are damaged
    except (EOFError, OSError, zlib.error, UnicodeDecodeError) as error:
        # make a channel
        channel = journal.warning("qed.measurements.census")
        # say so
        channel.log(f"the chunk records of '{granule}' are damaged, so it is left out: {error}")
        # and hand back nothing
        return None


def _chunks(*, granule: str, stream):
    """
    Generate the chunk records of {granule} in {stream} as (granule, dataset, stored, raw)
    """
    # go through them
    for record in csv.DictReader(stream):
        # skip the extra headers of runs that appended to the file
        if record["dataset"] == "dataset":
            # by moving on
            continue
        # hand off the ones that matter
        yield granule, record["dataset"], int(record["bytes"]), int(record["raw"])
    # all done
    return


def waste(*, source: str, rows: list, nearly: float = 0.01) -> dict:
    """
    Count, raster by raster, the chunks of the census in {source} that hold nothing but the fill:
    the chunks with the stored size of the smallest chunk, when that one is nearly empty, i.e.
    smaller than {nearly} of the raw size, and holds one value where the summaries in {rows} say
    what it holds; the result is by the name of the raster within its product
    """
    # what the summaries say the smallest chunk of each raster holds
    holds = {(row["granule"], row["dataset"]): row.get("smallest_holds") for row in rows}
    # the tally, by raster name
    tally = collections.defaultdict(
        lambda: {"rasters": 0, "written": 0, "stored": 0, "fill": 0, "fillBytes": 0, "checked": 0}
    )
    # the records of a granule come together, so take them a granule at a time
    for granule, records in itertools.groupby(chunks(source=source), key=lambda r: r[0]):
        # the sizes of the chunks of each of its rasters, and their raw size
        sizes = collections.defaultdict(list)
        raws = {}
        # go through its chunk records
        for _, dataset, stored, raw in records:
            # file each one with its raster
            sizes[dataset].append(stored)
            # and remember the raw size
            raws[dataset] = raw
        # go through its rasters
        for dataset, stored in sizes.items():
            # the entry of its name
            entry = tally[dataset.split(".", 1)[1]]
            # count it
            entry["rasters"] += 1
            entry["written"] += len(stored)
            entry["stored"] += sum(stored)
            # its smallest chunk
            smallest = min(stored)
            # what the census found in it, if it looked
            found = holds.get((granule, dataset)) or ""
            # a chunk that holds data, or one too large to be the fill
            if found in ("data", "unknown") or smallest >= nearly * raws[dataset]:
                # spares nothing
                continue
            # a census that looked has checked this raster
            entry["checked"] += found not in ("", "None")
            # the chunks that hold the same bytes as the smallest
            twins = stored.count(smallest)
            # are the ones a declared fill would have spared
            entry["fill"] += twins
            entry["fillBytes"] += twins * smallest
    # hand off the tally
    return dict(tally)


def value(*, row: dict, name: str):
    """
    The measure {name} of the raster in {row}, or {None} if the census did not record it
    """
    # the share of the written chunks that are nearly empty
    if name == "empty":
        # needs chunks that were written
        written = int(row["written"])
        # and is otherwise the ratio
        return int(row["empty"]) / written if written else None
    # the share of the chunk grid that was never written
    if name == "unwritten":
        # the ratio of the unwritten to all the chunks the tiling describes
        return 1 - int(row["written"]) / int(row["grid"])
    # the bytes the raster stores, in MiB
    if name == "stored_mib":
        # converted from bytes
        return int(row["stored"]) / 2**20
    # the bytes its nearly empty chunks store, in MiB, if the census recorded them
    if name == "empty_mib":
        # converted from bytes
        return int(row["empty_stored"]) / 2**20 if row.get("empty_stored") else None
    # the share of its pages that hold nothing but nearly empty chunks, if recorded
    if name == "empty_page_share":
        # needs pages
        return (
            int(row["empty_pages"]) / int(row["pages"])
            if row.get("empty_pages") and row.get("pages")
            else None
        )
    # the bytes stored by the chunks that hold nothing but the fill, in MiB, if recorded
    if name == "fill_mib":
        # converted from bytes
        return (
            int(row["fill_bytes"]) / 2**20
            if row.get("fill_bytes") not in (None, "", "None")
            else None
        )
    # the times, in ms, if recorded
    if name in ("decode_ms", "make_ms", "data_decode_ms", "encode_ms"):
        # from the time in seconds
        recorded = row.get(name[:-3] + "_s", "")
        # converted
        return 1e3 * float(recorded) if recorded not in ("", "None") else None
    # everything else is recorded as is
    recorded = row.get(name, "")
    # unless it is blank
    return float(recorded) if recorded not in ("", "None") else None


def values(*, rows: list, name: str) -> list:
    """
    The measure {name} of every raster in {rows} that has one
    """
    # collect them, leaving out the ones the census did not record
    return [v for v in (value(row=row, name=name) for row in rows) if v is not None]


def percentiles(*, numbers: list) -> tuple:
    """
    The 10th percentile, the median, the 90th percentile, and the maximum of {numbers}, or
    {None} if there are none
    """
    # without numbers
    if not numbers:
        # there is nothing to report
        return None
    # in order
    ordered = sorted(numbers)
    # the value at a fraction of the way through
    at = lambda fraction: ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]
    # hand off the four
    return at(0.1), statistics.median(ordered), at(0.9), ordered[-1]


def medians(*, rows: list, names: tuple) -> list:
    """
    The median of each of the measures {names} over the rasters in {rows}, or {None} for a
    measure none of them has
    """
    # go through the measures
    return [
        statistics.median(numbers) if numbers else None
        for numbers in (values(rows=rows, name=name) for name in names)
    ]


def histogram(*, rows: list, name: str) -> list:
    """
    Pool the histograms {name} of the rasters in {rows} into one, bin by bin
    """
    # the pooled counts
    pooled = []
    # go through the rows
    for row in rows:
        # skip the ones without the histogram
        if not row.get(name):
            # by moving on
            continue
        # the counts of this one
        counts = [int(count) for count in row[name].split("|")]
        # make room
        pooled += [0] * (len(counts) - len(pooled))
        # and add them in
        for index, count in enumerate(counts):
            # bin by bin
            pooled[index] += count
    # hand off the pooled counts
    return pooled


def settings(*, rows: list) -> dict:
    """
    Count the storage settings of the rasters in {rows}, by setting and value
    """

    # the tile is recorded as two columns
    def get(row, name):
        """
        The setting {name} of {row}
        """
        # the tile joins its two columns
        if name == "tile":
            # into one value
            return f"{row['tile_rows']}x{row['tile_cols']}"
        # whether the fill the library knows about is what the empty chunks hold
        if name == "fill_agrees":
            # is decided elsewhere
            return agrees(row=row)
        # the fill settings are missing from a census that predates them
        if name in FILL:
            # so they are blank there
            return row.get(name) or ""
        # everything else is recorded as is
        return row[name]

    # count each one
    return {name: collections.Counter(get(row, name) for row in rows) for name in SETTINGS}


def agrees(*, row: dict) -> str:
    """
    Whether the smallest chunk of the raster of {row}, when it holds one value, holds the fill
    value the library hands out for the chunks that were never written: "yes", "no", or blank
    when the chunk holds data or the census did not look
    """
    # what the chunk holds
    holds = row.get("smallest_holds") or ""
    # data, or something the census could not decode, or nothing recorded
    if holds in ("", "None", "data", "unknown"):
        # says nothing about the fill
        return ""
    # otherwise compare it with the library's fill, as rendered, so a nan matches a nan
    return "yes" if holds == row.get("hdf5_fill") else "no"


def raster(*, row: dict) -> str:
    """
    The name of the raster of {row} within its product, e.g. {L.A.HH}
    """
    # everything after the name of the product
    return row["dataset"].split(".", 1)[1]


def frequency(*, row: dict) -> str:
    """
    The frequency of the raster of {row}
    """
    # the third field of its name
    return row["dataset"].split(".")[2]


def scene(*, row: dict) -> str:
    """
    The scene of the granule of {row}: its id past the level, processing type, and product, which
    the products of one acquisition share
    """
    # drop the first four fields of the id
    return row["granule"].split("_", 4)[4]


def groups(*, rows: list, key) -> dict:
    """
    File the rows by the value {key} computes from each one
    """
    # the groups
    filed = collections.defaultdict(list)
    # go through the rows
    for row in rows:
        # and file each one
        filed[key(row=row)].append(row)
    # hand off the groups
    return dict(filed)


def rasters(*, rows: list) -> dict:
    """
    File the rows by the number of rasters in their product
    """
    # count the rasters of each product
    count = collections.Counter(row["granule"] for row in rows)
    # and file each row by the count of its product
    return groups(rows=rows, key=lambda row: count[row["granule"]])


def pairs(*, first: list, second: list) -> list:
    """
    Match the rasters of the census {first} with the ones of {second} that belong to the same
    scene and have the same name, as (first, second)
    """
    # index the first
    index = {(scene(row=row), raster(row=row)): row for row in first}
    # and match the second against it
    return [
        (index[key], row)
        for row, key in ((row, (scene(row=row), raster(row=row))) for row in second)
        if key in index
    ]


def compare(*, matched: list) -> list:
    """
    Compare the {matched} rasters measure by measure, as (name, label, median of the first,
    median of the second, share of the pairs in which the second is worse or {None})
    """
    # the comparison
    table = []
    # go through the measures
    for name, label, lower in MEASURES:
        # the pairs that have the measure on both sides
        both = [
            (a, b)
            for a, b in ((value(row=x, name=name), value(row=y, name=name)) for x, y in matched)
            if a is not None and b is not None
        ]
        # without any
        if not both:
            # there is nothing to compare
            continue
        # the share of the pairs in which the second is worse, for a measure that has a better
        worse = (
            sum(1 for a, b in both if (b > a if lower else b < a)) / len(both)
            if lower is not None
            else None
        )
        # add the row
        table.append(
            (
                name,
                label,
                statistics.median(a for a, _ in both),
                statistics.median(b for _, b in both),
                worse,
            )
        )
    # hand off the comparison
    return table


def markdown(*, headers: tuple, rows: list) -> list:
    """
    Render a table with {headers} and {rows} as the lines of a Markdown table
    """

    # render a cell
    def cell(entry):
        """
        Render one {entry} of the table
        """
        # nothing is blank
        if entry is None:
            # so render it that way
            return ""
        # large numbers are rounded to whole ones
        if isinstance(entry, float) and abs(entry) >= 100:
            # which keeps them out of scientific notation
            return f"{entry:.0f}"
        # the rest get three significant figures
        if isinstance(entry, float):
            # which keeps the columns readable
            return f"{entry:.3g}"
        # everything else is rendered as is
        return str(entry)

    # the header, the separator, and the rows
    return (
        ["| " + " | ".join(headers) + " |"]
        + ["|" + "|".join("---" for _ in headers) + "|"]
        + ["| " + " | ".join(cell(entry) for entry in row) + " |" for row in rows]
    )


# end of file
