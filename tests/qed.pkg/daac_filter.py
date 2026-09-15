#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the filter generator of the NISAR granule naming conventions: a partial specification
of the tokens matches the granule ids that agree with it and rejects the ones that do not
"""

# support
import qed

# the grammar
daac = qed.readers.nisar.daac
# a filter over the geocoded covariance products
filter = daac.filter(product="gcov")
# that pins the stack
filter.select(track=3, direction="A", frame=28)

# a granule in the stack
assert filter.match(
    "NISAR_L2_PR_GCOV_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001"
)
# a granule from another cycle of the same stack
assert filter.match(
    "NISAR_L2_PR_GCOV_007_003_A_028_2005_DHDH_A_20251017T093704_20251017T093739_P00410_N_F_J_001"
)
# a granule from another track
assert not filter.match(
    "NISAR_L2_PR_GCOV_005_004_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001"
)
# a granule from another frame
assert not filter.match(
    "NISAR_L2_PR_GCOV_005_003_A_029_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001"
)
# a granule of another product type
assert not filter.match(
    "NISAR_L2_PR_GSLC_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001"
)

# a filter that leaves every token open matches every granule of its type
loose = daac.filter(product="gcov")
loose.select()
assert loose.match(
    "NISAR_L2_PR_GCOV_005_004_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001"
)


# end of file
