# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed
import journal

# the recognizer
from .Registrar import Registrar as registrar

# the filter generator
from .Filter import Filter as filter

# the product descriptors
# precursor
from .Daphne import Daphne as daphne

# level 0
from .RRST import RRST as rrst
from .HST_DRT import HST_DRT as hst_drt
from .RRSD import RRSD as rrsd

# level 1
from .RIFG import RIFG as rifg
from .ROFF import ROFF as roff
from .RSLC import RSLC as rslc
from .RUNW import RUNW as runw

# level 2
from .GCOV import GCOV as gcov
from .GOFF import GOFF as goff
from .GSLC import GSLC as gslc
from .GUNW import GUNW as gunw

# level 3
from .SME2 import SME2 as sme2


# a convenience factory
def descriptor(granule):
    """
    Parse the {granule} id and generate a product descriptor
    """
    # make a registrar, ask it to parse the granule id, and generate a descriptor
    descriptor = registrar().parse(granule=granule)
    # verify that all went well
    if not descriptor:
        # make a channel
        channel = journal.warning("qed.readers.nisar.daac")
        # complain
        channel.line("unable to recognize the granule id")
        channel.line(granule)
        channel.line("as a NISAR standard data product")
        # flush
        channel.log()
    # and hand it off
    return descriptor


# end of file
