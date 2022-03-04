// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the mutator of the list of profile points
export const useSetPoints = () => {
    // get the flag mutator
    const { setPoints } = React.useContext(Context)

    // make a handler that adds a point to the pile
    const addPoint = p => {
        // update the list
        setPoints(old => {
            // make a copy
            const pile = [...old]
            // add the new point to it
            pile.push(p)
            // and return the new pile
            return pile
        })
        // all done
        return
    }

    // and return the handler
    return addPoint
}


// end of file
