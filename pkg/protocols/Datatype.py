# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2022 all rights reserved


# externals
import sys
# support
import qed
# my superclass
from .Specification import Specification


# the dataset layout
class Datatype(Specification, family="qed.datatypes"):
    """
    The datatype metadata
    """


    # public data
    byteswap = qed.properties.bool()
    byteswap.doc = "control whether byte swapping is necessary"

    channels = qed.properties.strings()
    channels.doc = "the names of the channels provided by this datatype"

    tile = qed.properties.tuple(schema=qed.properties.int())
    tile.doc = "the preferred shape of dataset subsets"


    # value processing hooks
    # the byte order is indicated by a single character prefix that must be stripped before
    # normal name resolution can take place; this is done in {pyre_convert}. the byte order
    # choice is applied after {pyre_instantiate} realizes the {datatype}
    @classmethod
    def pyre_convert(cls, value, **kwds):
        # if {value} is a string
        if isinstance(value, str):
            # check whether there is a byte order specifier
            if value[0] in cls.markers:
                # and strip it; we'll get a chance to handle this later
                value = value[1:]
            # run it through the table of aliases
            value = cls.aliases.get(value, value)
        # chain up
        return super().pyre_convert(value=value, **kwds)


    @classmethod
    def pyre_instantiate(cls, spec, component, name, locator):
        # chain up to build the {datatype} instance
        instance = super().pyre_instantiate(spec=spec,
                                           component=component, name=name, locator=locator)

        # the byte order marker is at the beginning of the {spec}
        marker = spec[0]
        # look it up and, if not specified, fall back to the default setting from the datatype
        instance.byteswap = cls.byteorder.get(marker, instance.byteswap)

        # return
        return instance


    # implementation details
    # the type alias table
    aliases = {
        # single precision numbers
        "r4": "qed.datatypes.real4",
        "real4": "qed.datatypes.real4",

        # double precision numbers
        "r8": "qed.datatypes.real8",
        "real8": "qed.datatypes.real8",

        # single precision complex numbers
        "c4": "qed.datatypes.complex4",
        "complex4": "qed.datatypes.complex4",

        # double precision complex numbers
        "c8": "qed.datatypes.complex8",
        "complex8": "qed.datatypes.complex8",
    }

    # the byte order truth table
    byteorder = {
        "<": sys.byteorder == "big",
        ">": sys.byteorder == "little",
        "!": sys.byteorder == "little",
        "@": False,
        "=": False,
    }

    # the set of byte order markers
    markers = tuple(byteorder.keys())


# end of file
