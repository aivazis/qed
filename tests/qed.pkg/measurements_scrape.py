#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the analysis of a scrape of a bucket on a scrape small enough to work out by hand: its
lists, the granules of each product by repeat cycle, the cycles every product has, and an even
sample of the granules of a cycle
"""

# externals
import os
import shutil

# support
import qed

# the analyses
scrape = qed.measurements.scrape

# an RSLC of cycle 31
single = "NISAR_L1_PR_RSLC_{cycle}_{track}_A_004_2005_DHDH_A_20260918T060359_20260918T060423_P05023_N_P_J_001"
# a GUNW whose reference acquisition is in cycle 13 and whose secondary is in cycle 14
pair = (
    "NISAR_L2_PR_GUNW_013_055_A_010_014_4000_SH_20260101T000110_20260101T000133"
    "_20260113T000110_20260113T000133_P05006_N_P_J_001"
)

# in a scratch folder
# the scratch folder, next to this driver, where the products stay for inspection
folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "measurements_scrape.scratch")
# start clean, by removing whatever a previous run left behind
shutil.rmtree(folder, ignore_errors=True)
# and make it
os.makedirs(folder)
# three RSLC of cycle 31, one of cycle 13, and one the parser does not recognize
with open(os.path.join(folder, "rslc.txt"), "w") as stream:
    # one per line
    stream.write(
        "\n".join(
            [single.format(cycle="031", track=f"{track:03}") for track in (1, 2, 3)]
            + [single.format(cycle="013", track="001"), "NISAR_L1_PR_RSLC_nonsense", ""]
        )
    )
# and one GUNW
with open(os.path.join(folder, "gunw.txt"), "w") as stream:
    # on its own line
    stream.write(pair + "\n")
# and a stream of raw telemetry, which the parser recognizes but which has no repeat cycle
with open(os.path.join(folder, "rrst.txt"), "w") as stream:
    # on its own line
    stream.write("NISAR_L0_RRST_VC25_20250819T233022_20250819T233027_P00408_J_001\n")

# the lists are named after the products
assert scrape.lists(scrape=folder) == ["gunw", "rrst", "rslc"]
# a product without a repeat cycle is counted under none
assert scrape.cycles(scrape=folder, products=["rrst"]) == {"rrst": {None: 1}}
# the counts by cycle, with a pair counted under the cycle of its reference acquisition
counts = scrape.cycles(scrape=folder, products=["rslc", "gunw"])
assert counts["rslc"] == {31: 3, 13: 1, None: 1}
assert counts["gunw"] == {13: 1}
# the one cycle both products have
assert scrape.complete(counts=counts) == [13]
# which a product without cycles leaves alone
counts.update(scrape.cycles(scrape=folder, products=["rrst"]))
assert scrape.complete(counts=counts) == [13]
# an even sample of two of the three RSLC of cycle 31: the first and the last
picked = scrape.spread(scrape=folder, product="rslc", cycle=31, count=2)
assert [granule.split("_")[5] for granule in picked] == ["001", "003"]
# a sample of one is the one in the middle
picked = scrape.spread(scrape=folder, product="rslc", cycle=31, count=1)
assert [granule.split("_")[5] for granule in picked] == ["002"]
# and a sample larger than the cycle is the whole cycle
assert len(scrape.spread(scrape=folder, product="rslc", cycle=31, count=10)) == 3


# end of file
