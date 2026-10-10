// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// the engine that draws the tiles of the active view, and whether its channel's pipeline can
export const useEngine = () => {
    // grab them
    const { engine, flowable } = React.useContext(Context)
    // and return them
    return { engine, flowable }
}


// end of file
