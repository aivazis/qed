// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// toggle the measure layer over this viewport
export const useToggleMeasureLayer = viewport => {
    // grab the measure layer mutator from context
    const { setMeasureLayer, setPixelPath } = React.useContext(Context)

    // a handler that toggles whether the measure layer is visible
    const toggle = () => {
        // toggle
        setMeasureLayer(old => {
            // make a copy of the measure layer status table
            const table = [...old]
            // toggle the entry that corresponds to this viewport
            table[viewport] = !table[viewport]
            // and return the new table
            return table
        })
        // on toggle, clear the pixel path as well
        setPixelPath(old => {
            // make a copy of the paths
            const paths = [...old]
            // clear out the one that corresponds to {viewport}
            paths[viewport] = []
            // and return the new pile
            return paths
        })
        // all done
        return
    }

    // return the toggle
    return toggle
}


// end of file
