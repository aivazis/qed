// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// set the zoom level of the active viewport
export const useSetZoomLevel = () => {
    // grab the active viewport and the zoom level table mutator
    const { activeViewport, setZoom } = React.useContext(Context)

    // a handler that sets the zoom level of the active viewport
    const set = (value) => {
        // update the zoom table
        setZoom(old => {
            // make a copy of the old table
            const table = [...old]
            // adjust the entry that corresponds to the active view
            table[activeViewport] = Math.round(value)
            // return the new table
            return table
        })
        // all done
        return
    }

    // return the handler
    return set
}


// end of file
