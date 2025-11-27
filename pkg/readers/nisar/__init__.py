# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# support
import qed

# publish the readers
from .L0A import L0A as l0a

# level 0
from .RRSD import RRSD as rrsd

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
def metadata(uri, credentials, **kwds):
    """
    Build a metadata object
    """
    # instantiate the object
    metadata = qed.readers.metadata()
    # attach the uri
    metadata.uri = uri
    # open the file
    #
    # MGA: we are here...
    #
    data = qed.h5.read(uri=uri, credentials=credentials)
    # set the product type
    metadata.product = data.science.LSAR.identification.productType.lower()
    # attempt to
    try:
        # get the product version
        metadata.version = data.science.LSAR.identification.productVersion
    # if something goes wrong
    except AttributeError:
        # no worries
        pass
    # attempt to
    try:
        # get the product specification version
        metadata.spec = data.science.LSAR.identification.productSpecificationVersion
    # if something goes wrong
    except AttributeError:
        # no worries
        pass
    # that's all we know, for now
    return metadata


# end of file
