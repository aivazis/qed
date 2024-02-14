# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2024 all rights reserved


# support
import qed

# publish the readers
from .L0A import L0A as l0a

# level 1
from .RSLC import RSLC as rslc
from .ROFF import ROFF as roff
from .RIFG import RIFG as rifg
from .RUNW import RUNW as runw

# level 2
from .GSLC import GSLC as gslc
from .GOFF import GOFF as goff
from .GUNW import GUNW as gunw
from .GCOV import GCOV as gcov


# metadata factory
def metadata(uri):
    """
    Build a metadata object
    """
    # instantiate the object
    metadata = qed.readers.metadata()
    # attach the uri
    metadata.uri = uri
    # open the file
    data = qed.h5.read(uri=uri)
    # set the product type
    metadata.product = data.science.LSAR.identification.productType.lower()
    # that's all we know, for now
    return metadata


# end of file
