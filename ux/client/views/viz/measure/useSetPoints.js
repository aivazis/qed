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


    // make a handler that displaces a collection of {nodes} by a given {delta}
    const movePoints = ({ nodes, delta }) => {
        // update the list
        setPoints(old => {
            // make a copy
            const pile = [...old]

            // go through the node ids
            nodes.forEach(node => {
                // get the coordinates of this node
                let [x, y] = pile[node]
                // displace them
                x += delta.x
                y += delta.y
                // and reattach
                pile[node] = [x, y]
                // get the next one
                return
            })

            // and return the updated pile
            return pile
        })
        // all done
        return
    }

    // and return the handler
    return { addPoint, movePoints }
}


// end of file
