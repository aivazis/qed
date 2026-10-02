// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Context } from './context'


// access the configuration and the geometry of the histogram
export const useConfig = () => {
    // pull what i need from {context}
    const {
        counts, domain, width, height, log, label, marker, format, ticks, unit,
        gutter, headroom, left, room, reach, bin, tallest, scale, at, base,
    } = React.useContext(Context)
    // and publish
    return {
        counts, domain, width, height, log, label, marker, format, ticks, unit,
        gutter, headroom, left, room, reach, bin, tallest, scale, at, base,
    }
}


// end of file
