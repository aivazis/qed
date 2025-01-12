// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// storage for the refs to the {mosaic} placemats that frame the visible part of the data
export const useViewports = () => {
    // grab the array of refs from my context
    const { activeViewport, setActiveViewport, viewports } = React.useContext(Context)

    // make a handler that activates a viewport
    const activate = viewport => () => {
        // activate the viewport
        setActiveViewport(viewport)
        // all done
        return
    }

    // and return its current pile
    return { activeViewport, setActiveViewport, viewports: viewports.current, activate }
}


// end of file
