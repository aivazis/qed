#!/usr/bin/env python3
# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the names the product families propose for the readers of their products: a NISAR
granule is named after its product, its acquisition fields in granule order, and its release,
and every other file after its name, made fit to be a single level of a pyre name
"""

# support
import qed

# the NISAR proposals
nisar = qed.readers.nisar.nickname
# the proposals of the families without naming conventions of their own
generic = qed.readers.nickname

# a product of one acquisition: cycle, track, direction, and frame
assert (
    nisar(
        uri="s3://bucket/L2/NISAR_L2_PR_GSLC_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001.h5"
    )
    == "gslc-005_003_A_028-P00410"
)
# a product of a pair: reference cycle, track, direction, frame, and secondary cycle
assert (
    nisar(
        uri="file:/data/NISAR_L1_PR_RIFG_005_003_A_155_007_4000_SH_20250923T104926_20250923T105002_20251017T104924_20251017T105002_P05000_N_F_J_001.h5"
    )
    == "rifg-005_003_A_155_007-P05000"
)
# a level 0 product has no frame: cycle, track, and direction
assert (
    nisar(
        uri="file:/data/NISAR_L0_PR_RRSD_002_143_D_001S_20250821T071148_20250821T071641_P00408_F_J_001.h5"
    )
    == "rrsd-002_143_D-P00408"
)
# a telemetry stream has no pass or location, so it is named after its file
assert (
    nisar(uri="file:/data/NISAR_L0_RRST_VC24_20250805T022853_20250805T022858_P00407_J_001.bin")
    == "NISAR_L0_RRST_VC24_20250805T022853_20250805T022858_P00407_J_001"
)
# and so is a file whose name is not a granule id
assert nisar(uri="file:/data/scene.h5") == "scene"

# any other file is named after its file name, without the extension
assert generic(uri="file:/tmp/x/raster.bin") == "raster"
# whose dots would make levels and whose punctuation does not belong
assert generic(uri="file:/d/nisar.89e8cbe.A.sci") == "nisar_89e8cbe_A"
assert generic(uri="file:/d/my file (2).int") == "my_file__2_"
# a path without a scheme works too
assert generic(uri="/tmp/x/a.int") == "a"
# and a file with nothing but an extension still gets a name
assert generic(uri="file:/d/.bin") == "reader"


# end of file
