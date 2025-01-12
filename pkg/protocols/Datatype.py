# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


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
        """
        Translate the component specification in {value} into canonical form; invoked during value
        processing
        """
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
        """
        Invoke the {component} constructor to build a new instance
        """
        # chain up to build the {datatype} instance
        instance = super().pyre_instantiate(
            spec=spec, component=component, name=name, locator=locator
        )

        # if the {spec} is a string
        if isinstance(spec, str):
            # the byte order marker is at the beginning of the {spec}
            marker = spec[0]
            # look it up and, if not specified, fall back to the default setting from the datatype
            instance.byteswap = cls.byteorder.get(marker, instance.byteswap)

        # return
        return instance

    # implementation details
    # the type alias table
    aliases = {
        # bytes
        "c": "qed.datatypes.char",
        "char": "qed.datatypes.char",
        # signed integers
        "i1": "qed.datatypes.int8",
        "int8": "qed.datatypes.int8",
        "i2": "qed.datatypes.int16",
        "int16": "qed.datatypes.int16",
        "i4": "qed.datatypes.int32",
        "int32": "qed.datatypes.int32",
        "i8": "qed.datatypes.int64",
        "int64": "qed.datatypes.int64",
        # unsigned integers
        "u1": "qed.datatypes.uint8",
        "uint8": "qed.datatypes.uint8",
        "u2": "qed.datatypes.uint16",
        "uint16": "qed.datatypes.uint16",
        "u4": "qed.datatypes.uint32",
        "uint32": "qed.datatypes.uint32",
        "u8": "qed.datatypes.uint64",
        "uint64": "qed.datatypes.uint64",
        # single precision numbers
        "r4": "qed.datatypes.real32",
        "real32": "qed.datatypes.float",
        "float32": "qed.datatypes.float",
        # double precision numbers
        "r8": "qed.datatypes.double",
        "real64": "qed.datatypes.double",
        "float64": "qed.datatypes.double",
        # single precision complex numbers
        "c8": "qed.datatypes.complex64",
        "complex64": "qed.datatypes.complex64",
        # double precision complex numbers
        "c16": "qed.datatypes.complex128",
        "complex128": "qed.datatypes.complex128",
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
