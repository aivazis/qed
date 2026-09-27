#!/usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the analysis of the results of a census on summaries small enough to work out by hand: the
measures derived from the recorded columns, the percentiles, the groups, the pairing of the rasters
of the same scene in two censuses, and their comparison
"""

# support
import qed

# the analyses
census = qed.measurements.census


def close(computed, expected):
    """
    Check that the {computed} numbers match the {expected} ones, to within rounding
    """
    # the ones that are not numbers must match exactly, and the numbers to within rounding
    return len(computed) == len(expected) and all(
        c == e if not isinstance(e, float) else abs(c - e) < 1e-12
        for c, e in zip(computed, expected)
    )


def row(granule, dataset, once, locality, written, empty, grid=100, stored=2**20):
    """
    Make the summary of one raster, with the columns the analyses read
    """
    # the recorded columns
    return {
        "granule": granule,
        "dataset": f"product.{dataset}",
        "once": str(once),
        "joint": "1.05",
        "alone": "4",
        "fill_mean": "0.9",
        "locality": str(locality),
        "compression": "2",
        "written": str(written),
        "empty": str(empty),
        "grid": str(grid),
        "stored": str(stored),
        "size_histogram": "1|2",
    }


# the scene both censuses measured, and the products of it
scene = "031_001_A_004_2005_DHDH_A_20260918T060359_20260918T060423_P05023_N_P_J_001"
rslc = f"NISAR_L1_PR_RSLC_{scene}"
gslc = f"NISAR_L2_PR_GSLC_{scene}"

# the first census: two rasters of the RSLC, with nothing empty
first = [row(rslc, "L.A.HH", 1.1, 0.9, 100, 0), row(rslc, "L.A.HV", 1.1, 0.9, 100, 0)]
# the second: the same rasters of the GSLC, with a quarter of their written chunks nearly empty,
# and a raster the first does not have
second = [
    row(gslc, "L.A.HH", 1.4, 0.6, 80, 20),
    row(gslc, "L.A.HV", 1.3, 0.7, 80, 20),
    row(gslc, "L.B.HH", 1.7, 0.5, 40, 10),
]

# the derived measures
assert census.value(row=second[0], name="empty") == 0.25
assert abs(census.value(row=second[0], name="unwritten") - 0.2) < 1e-12
assert census.value(row=second[0], name="stored_mib") == 1.0
assert census.value(row=second[0], name="once") == 1.4
# a raster with no written chunks has no share of empty ones
assert census.value(row=row(gslc, "L.B.HV", 1, 1, 0, 0), name="empty") is None

# the percentiles of ten numbers
p10, median, p90, top = census.percentiles(numbers=[float(i) for i in range(10)])
assert (p10, median, p90, top) == (1.0, 4.5, 9.0, 9.0)
# and of nothing
assert census.percentiles(numbers=[]) is None

# the names the analyses derive from a summary
assert census.raster(row=second[2]) == "L.B.HH"
assert census.frequency(row=second[2]) == "B"
assert census.scene(row=second[0]) == scene

# the groups by frequency
byfrequency = census.groups(rows=second, key=census.frequency)
assert {key: len(group) for key, group in byfrequency.items()} == {"A": 2, "B": 1}
# and by the number of rasters in the product
assert list(census.rasters(rows=second)) == [3]
# the medians of a group
assert close(census.medians(rows=byfrequency["A"], names=("once", "empty")), [1.35, 0.25])

# the pairs: the two rasters the censuses share, and not the one only the second has
matched = census.pairs(first=first, second=second)
assert [(census.raster(row=a), census.raster(row=b)) for a, b in matched] == [
    ("L.A.HH", "L.A.HH"),
    ("L.A.HV", "L.A.HV"),
]
# their comparison, by measure
table = {name: (a, b, worse) for name, _, a, b, worse in census.compare(matched=matched)}
# the second reads worse alone in both pairs
assert close(table["once"], (1.1, 1.35, 1.0))
# its locality is lower in both
assert close(table["locality"], (0.9, 0.65, 1.0))
# its empty chunks are more in both
assert close(table["empty"], (0.0, 0.25, 1.0))
# and a measure with no better has no share of worse
assert table["compression"][2] is None

# the pooled histogram
assert census.histogram(rows=second, name="size_histogram") == [3, 6]

# a table in Markdown
assert census.markdown(headers=("a", "b"), rows=[(1, 0.12345), ("x", None), (2, 1373.6)]) == [
    "| a | b |",
    "|---|---|",
    "| 1 | 0.123 |",
    "| x |  |",
    "| 2 | 1374 |",
]


# end of file
