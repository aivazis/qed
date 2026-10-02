# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


def canonical(*, prefix: str, descriptor) -> str:
    """
    Build the key of the product described by {descriptor} in a bucket that follows the
    canonical layout of the NISAR products, under {prefix}: a folder for each product, named
    after its stage, band, and type, then one for each year, month, and day of its time mark,
    and one for each granule, which holds the product file
    """
    # the time mark of the product: its acquisition, or the reference acquisition of a pair
    mark = descriptor.mark
    # assemble the key
    return (
        # under the prefix
        f"{prefix}"
        # the folder of the product
        f"{descriptor.stage}_{descriptor.band}_{descriptor.product}/"
        # the date of its time mark
        f"{mark.year}/{mark.month:02}/{mark.day:02}/"
        # the folder of the granule
        f"{descriptor.gid}/"
        # and the product file
        f"{descriptor.filename}"
    )


# end of file
