# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# support
import qed

# the granule naming conventions
from . import daac

# publish the readers
from .Pyramid import Pyramid as pyramid
from .H5 import H5 as h5

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

# the slicer that reads windows of the rasters of products
from .Fetch import Fetch as fetch

# the factories that recolor the cells with no data, and the cells the masks flag
from .Absence import Absence as absence
from .GUNWScreen import GUNWScreen as gunwScreen
from .GCOVScreen import GCOVScreen as gcovScreen

# the colormaps that show the masks by themselves
from .GUNWPalette import GUNWPalette as gunwPalette
from .GCOVPalette import GCOVPalette as gcovPalette

# contribute the flow nodes of products to the catalogs recipes are staged against, when the
# extension that holds them was built
if qed.libqed is not None:
    # register its catalog
    qed.flow.recipes.register(catalog=qed.libqed.nisar.flow.catalog())


# the name of a reader
def nickname(uri: str, **kwds) -> str:
    """
    Propose a name for the reader of the product at {uri}, made from its granule id
    """
    # find the file the {uri} points to
    address = qed.primitives.uri.parse(uri).address
    # its name without the extension is the granule id, if it follows the conventions
    granule = qed.primitives.path(address).stem
    # take it apart
    fields = daac.registrar().fields(granule=granule)
    # a file whose name is not a granule id
    if fields is None:
        # gets the name any file would
        return qed.readers.nickname(uri=uri, **kwds)
    # a product of one acquisition has a cycle, a product of a pair a reference cycle
    cycle = "cycle" if "cycle" in fields else "referenceCycle"
    # a granule without a cycle, a track, or a pass direction, such as a raw telemetry stream,
    if cycle not in fields or "track" not in fields or "direction" not in fields:
        # gets the name any file would
        return qed.readers.nickname(uri=uri, **kwds)
    # the acquisition, in the order the granule id spells it: the cycle, the track, the pass
    # direction, the frame along the track, for the products that have one, and the secondary
    # cycle of a pair
    order = (cycle, "track", "direction", "frame", "secondaryCycle")
    # pick the ones this granule has
    acquisition = "_".join(fields[field] for field in order if field in fields)
    # the composite release id is spelled out by five fields
    crid = "".join(fields[field] for field in ("environment", "phase", "major", "minor", "patch"))
    # assemble the name: the product, the acquisition, and the release
    return f"{fields['product'].lower()}-{acquisition}-{crid}"


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
