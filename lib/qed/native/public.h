// -*- c++ -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved

// code guard
#pragma once

// external packages
#include "externals.h"
// get the forward declarations
#include "forward.h"

// published type aliases; this is the file you are looking for...
#include "api.h"

// implementation
// channels
#include "channels/amplitude.h"
#include "channels/complex.h"
#include "channels/imaginary.h"
#include "channels/phase.h"
#include "channels/real.h"
#include "channels/value.h"
#include "channels/magnitude.h"
#include "channels/MeanPower.h"
#include "channels/Coherence.h"
#include "channels/spectrum.h"

// the fourier transform
#include "fft.h"
// and the steps that can precede it: the fill that contributes nothing
#include "finite.h"
// and the taper
#include "hann.h"
// profile
#include "profile.h"
// statistics
#include "stats.h"


// end of file
