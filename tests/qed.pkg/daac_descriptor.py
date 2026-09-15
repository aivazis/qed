#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


"""
Check the parser of the NISAR granule naming conventions: every standard product id is
recognized, its fields are extracted, and the id is reconstructed from them exactly
"""

# support
import qed

# the sample granules, one per standard product type
granules = [
    "NISAR_S198_WFF_WG5_M00_P01840_R00_C01_G00_2025_338_23_25_37_039323226.vc29",
    "NISAR_L0_PR_HST_DRT_012_023_A_20251210T221749_20251210T222224_P05000_J_001",
    "NISAR_L0_RRST_VC24_20250805T022853_20250805T022858_P00407_J_001",
    "NISAR_L0_PR_RRSD_002_143_D_001S_20250821T071148_20250821T071641_P00408_F_J_001",
    "NISAR_L1_PR_RSLC_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001",
    "NISAR_L2_PR_GSLC_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001",
    "NISAR_L2_PR_GCOV_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001",
    "NISAR_L3_PR_SME2_005_003_A_028_2005_DHDH_A_20250923T093702_20250923T093738_P00410_N_F_J_001",
    "NISAR_L1_PR_RIFG_005_003_A_155_007_4000_SH_20250923T104926_20250923T105002_20251017T104924_20251017T105002_P05000_N_F_J_001",
    "NISAR_L1_PR_RUNW_005_003_A_155_007_4000_SH_20250923T104926_20250923T105002_20251017T104924_20251017T105002_P05000_N_F_J_001",
    "NISAR_L1_PR_ROFF_005_003_A_155_007_4000_SH_20250923T104926_20250923T105002_20251017T104924_20251017T105002_P05000_N_F_J_001",
    "NISAR_L2_PR_GUNW_005_003_A_028_007_2000_SH_20250923T093702_20250923T093738_20251017T093704_20251017T093739_P05000_N_F_J_001",
    "NISAR_L2_PR_GOFF_005_003_A_155_007_4000_SH_20250923T104926_20250923T105002_20251017T104924_20251017T105002_P05000_N_F_J_001",
]

# the grammar
daac = qed.readers.nisar.daac
# go through the samples
for granule in granules:
    # parse the id
    descriptor = daac.descriptor(granule=granule)
    # it is recognized
    assert descriptor
    # and reconstructed exactly
    assert descriptor.gid == granule

# a single acquisition product knows its stack and its acquisition time
gcov = daac.descriptor(granule=granules[6])
assert (gcov.track, gcov.direction, gcov.frame) == (3, "A", 28)
assert str(gcov.mark) == "2025-09-23 09:37:02"

# a pair product carries the same stack and marks time by its reference acquisition
gunw = daac.descriptor(granule=granules[11])
assert (gunw.track, gunw.direction, gunw.frame) == (3, "A", 28)
assert str(gunw.mark) == "2025-09-23 09:37:02"
assert str(gunw.referenceBegin) == "2025-09-23 09:37:02"

# a level 0 product has a track and a direction but no frame
rrsd = daac.descriptor(granule=granules[3])
assert (rrsd.track, rrsd.direction) == (143, "D")
assert not hasattr(rrsd, "frame")

# an id that does not follow the conventions is not recognized
assert daac.registrar().grok("not_a_granule")["product"] == "unknown"


# end of file
