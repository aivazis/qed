# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2025 all rights reserved


# publish
# characters
from .Char import Char as char

# integers
from .Int8 import Int8 as int8
from .Int16 import Int16 as int16
from .Int32 import Int32 as int32
from .Int64 import Int64 as int64
from .UInt8 import UInt8 as uint8
from .UInt16 import UInt16 as uint16
from .UInt32 import UInt32 as uint32
from .UInt64 import UInt64 as uint64

# real numbers
from .Float import Float as float
from .Double import Double as double

# complex numbers
from .ComplexFloat import ComplexFloat as complex64
from .ComplexDouble import ComplexDouble as complex128

# aliases
float32 = float
float64 = double
real32 = float
real64 = double

# gdal
# NYI: cint16, cint32
byte = char
cfloat32 = complex64
cfloat64 = complex128

# end of file
