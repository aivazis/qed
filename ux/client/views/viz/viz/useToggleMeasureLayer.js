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
    const { setMeasureLayer } = React.useContext(Context)

    // a handler that toggles whether the measure layer is visible
    const toggle = () => {
        // toggle
        setMeasureLayer(old => {
            // make a copy
            const table = [...old]
            // toggle the entry that corresponds to this viewport
            table[viewport] = !table[viewport]
            // and return the new table
            return table
        })
        // all done
        return
    }

    // return the toggle
    return toggle
}


// end of file
