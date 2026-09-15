#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check that an earth archive is its query: the traits assemble into the query builder
parameters, a collection alone lists nothing, and a constrained archive lists the page its
query answers, one item per granule with the payload location the readers understand
"""

# support
import journal
import qed


def granule(name):
    """
    Build a catalog record with the parts of the repository's shape the archive reads
    """
    # assemble the record and return it
    return {
        "meta": {"native-id": name},
        "umm": {
            "DataGranule": {
                "ArchiveAndDistributionInformation": [{"Name": f"{name}.h5", "SizeInBytes": 7}]
            },
            "RelatedUrls": [
                {"URL": f"https://daac/{name}.h5", "Type": "GET DATA"},
                {"URL": f"s3://bucket/{name}/{name}.h5", "Type": "GET DATA VIA DIRECT ACCESS"},
                {"URL": f"s3://browse/{name}.png", "Type": "GET RELATED VISUALIZATION"},
            ],
        },
    }


# the refusal of an unconstrained listing is reported on a warning channel; keep it quiet here
journal.warning("qed.archives.earth.contents").deactivate()

# an archive that names a collection and nothing else
bare = qed.archives.earth(name="earth_bare", collection="NISAR_L2_GCOV_PROVISIONAL_V1")
# is not constrained
assert not bare.constrained
# its query is the collection
assert bare.query() == {"short_name": "NISAR_L2_GCOV_PROVISIONAL_V1"}
# and it lists nothing
assert bare.contents(uri=bare.uri) == []

# an archive over crete, open ended in time, capped
crete = qed.archives.earth(
    name="earth_crete",
    uri="earth:crete",
    collection="NISAR_L2_GCOV_PROVISIONAL_V1",
    conceptId="C1234-ASF",
    count=2,
    begin="2026-01-01",
    polygon=[(23.4, 35.0), (26.4, 35.0), (26.4, 35.7), (23.4, 35.7)],
)
# is constrained
assert crete.constrained
# assemble its query
query = crete.query()
# the collection is named both ways
assert query["short_name"] == "NISAR_L2_GCOV_PROVISIONAL_V1"
assert query["concept_id"] == "C1234-ASF"
# the window is open at the end
assert query["temporal"] == ("2026-01-01", None)
# the polygon is closed
assert query["polygon"] == [(23.4, 35.0), (26.4, 35.0), (26.4, 35.7), (23.4, 35.7), (23.4, 35.0)]
# and nothing else made it in
assert sorted(query) == ["concept_id", "polygon", "short_name", "temporal"]

# the page the query answers: two granules of one stack on different dates, one of another
# stack, and one whose id the grammar does not know
g1 = "NISAR_L2_PR_GCOV_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001"
g2 = "NISAR_L2_PR_GCOV_007_003_A_028_2005_DHDH_A_20251017T093704_20251017T093739_P00410_N_F_J_001"
g3 = "NISAR_L2_PR_GCOV_005_004_D_012_2005_DHDH_A_20250924T210000_20250924T210030_P00410_N_F_J_001"
g4 = "not_a_nisar_granule"
page = [granule(name=g2), granule(name=g1), granule(name=g3), granule(name=g4)]
# the grammar reports the id it does not know on a warning channel; keep it quiet here
journal.warning("qed.readers.nisar.daac").deactivate()
# a tally of the queries that were run
runs = []


# an engine that checks what it is asked and answers with the canned page
def engine(query, count):
    # the query is the archive's
    assert query == crete.query()
    # the cap is the archive's
    assert count == 2
    # tally
    runs.append(query)
    # answer
    return 52, page


# mount the archive over the canned engine
crete.mount(engine=engine)
# the root lists the stacks, then the granule that has no stack
assert crete.contents(uri=crete.uri) == [
    ("003_A_028", "earth:crete/003_A_028", True),
    ("004_D_012", "earth:crete/004_D_012", True),
    (g4, "s3://daac@us-west-2/bucket/not_a_nisar_granule/not_a_nisar_granule.h5", False),
]
# the query ran once
assert len(runs) == 1
# the catalog count is on record
assert crete.fs.hits == 52
# a stack lists its acquisition dates
assert crete.contents(uri=qed.primitives.uri.parse("earth:crete/003_A_028")) == [
    ("2025-09-23", "earth:crete/003_A_028/2025-09-23", True),
    ("2025-10-17", "earth:crete/003_A_028/2025-10-17", True),
]
# a date lists its granules, with the payload location the readers understand
assert crete.contents(uri=qed.primitives.uri.parse("earth:crete/003_A_028/2025-10-17")) == [
    (g2, f"s3://daac@us-west-2/bucket/{g2}/{g2}.h5", False),
]
# the page in hand answered both without running the query again
assert len(runs) == 1
# a folder that is not on the page lists nothing
journal.warning("qed.archives.earth.contents").deactivate()
assert crete.contents(uri=qed.primitives.uri.parse("earth:crete/999_A_001")) == []
# listing the root again refreshes the page
crete.contents(uri=crete.uri)
assert len(runs) == 2


# end of file
