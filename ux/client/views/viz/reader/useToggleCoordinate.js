// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// toggle the {coordinate} as the value for {axis}
export const useToggleCoordinate = (axis, coordinate) => {
    // get the selector ref
    const { selector } = React.useContext(Context)

    // make the toggle
    const toggle = () => {
        // access the map
        const coordinates = selector.current
        // get the current value for this {axis}
        const currentCoordinate = coordinates.get(axis)
        // if i'm the current selection
        if (currentCoordinate === coordinate) {
            // remove this choice from the map
            coordinates.delete(axis)
        } else {
            // otherwise, pick me
            coordinates.set(axis, coordinate)
        }
        // all done
        return
    }

    // all done
    return toggle
}


// end of file
