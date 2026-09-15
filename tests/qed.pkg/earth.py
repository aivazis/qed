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

# the page the query answers
page = [granule(name="g2"), granule(name="g1")]


# an engine that checks what it is asked and answers with the canned page
def engine(query, count):
    # the query is the archive's
    assert query == crete.query()
    # the cap is the archive's
    assert count == 2
    # answer
    return 52, page


# mount the archive over the canned engine
crete.mount(engine=engine)
# list its contents
items = crete.contents(uri=crete.uri)
# one item per granule, sorted, with the payload location the readers understand
assert items == [
    ("g1", "s3://daac@us-west-2/bucket/g1/g1.h5", False),
    ("g2", "s3://daac@us-west-2/bucket/g2/g2.h5", False),
]
# the catalog count is on record
assert crete.fs.hits == 52


# end of file
