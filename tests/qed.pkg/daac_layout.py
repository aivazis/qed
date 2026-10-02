#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the key of a product in a bucket that follows the canonical layout of the NISAR products,
for a product of one acquisition and for a product of a pair, which is filed under its reference
acquisition; both keys are ones the operations bucket holds
"""

# support
import qed

# the parser
registrar = qed.readers.nisar.daac.registrar()
# the key builder
canonical = qed.readers.nisar.daac.canonical

# a product of one acquisition
rslc = "NISAR_L1_PR_RSLC_031_098_A_144_4005_SHSH_A_20260925T005205_20260925T005242_P05023_N_F_J_001"
# is filed under its product, the date it was acquired, and its granule
assert (
    canonical(prefix="products/", descriptor=registrar.parse(rslc))
    == f"products/L1_L_RSLC/2026/09/25/{rslc}/{rslc}.h5"
)

# a product of a pair
gunw = (
    "NISAR_L2_PR_GUNW_013_055_A_010_014_4000_SH_20260101T000110_20260101T000133"
    "_20260113T000110_20260113T000133_P05006_N_P_J_001"
)
# is filed under the date of its reference acquisition
assert (
    canonical(prefix="products/", descriptor=registrar.parse(gunw))
    == f"products/L2_L_GUNW/2026/01/01/{gunw}/{gunw}.h5"
)


# end of file
