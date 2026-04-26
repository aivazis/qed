# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
# (c) 1998-2026 all rights reserved


# channels suitable for a real dataset
from .Magnitude import Magnitude as abs
from .Value import Value as value
from .UnwrappedPhase import UnwrappedPhase as unwrapped
from .UnwrappedPhaseMasked import UnwrappedPhaseMasked as unwrappedMasked

# channels suitable for a complex dataset
from .Amplitude import Amplitude as amplitude
from .Complex import Complex as complex
from .Imaginary import Imaginary as imaginary
from .Phase import Phase as phase
from .Real import Real as real

# channels suitable for a BFPQ encoded complex dataset
from .BFPQAmplitude import BFPQAmplitude as amplitudeBFPQ
from .BFPQComplex import BFPQComplex as complexBFPQ
from .BFPQImaginary import BFPQImaginary as imaginaryBFPQ
from .BFPQPhase import BFPQPhase as phaseBFPQ
from .BFPQReal import BFPQReal as realBFPQ

# bitmasks
from .Raw import Raw as raw


# end of file
