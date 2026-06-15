// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// read and toggle a viewport's opt-in to live sync, a client-only preference
export const useLive = (viewport) => {
    // grab the live-sync state from my context
    const { live, toggleLive } = React.useContext(Context)
    // whether this viewport is opted in
    const enabled = live.has(viewport)
    // a handler that flips this viewport's opt-in
    const toggle = () => toggleLive(viewport)
    // hand them back
    return { enabled, toggle }
}


// end of file
