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
export const useSetPixelPath = (viewport = null) => {
    // get the flag mutator
    const { activeViewport, setPixelPath } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport

    // make a handler that adds a point to the pile
    // the optional {pos} adds the point {p} before the supplied position, otherwise the point is
    // pushed to the end
    const add = (p, pos = null) => {
        // update the list
        setPixelPath(old => {
            // make a copy of the whole pile
            const pile = [...old]
            // get the portion that corresponds to this {viewport}
            const mine = pile[viewport]
            // add the new point to it
            pos === null ? mine.push(p) : mine.splice(pos, 0, p)
            // and return the new pile
            return pile
        })
        // all done
        return
    }

    // make a handler that adds a point to the path by splitting an existing leg in two
    // don't call this before making sure that both {node} and {node+1} are in the path
    const split = (node) => {
        // update the list
        setPixelPath(old => {
            // make a copy
            const pile = [...old]
            // and find the portion that corresponds to this {viewport}
            const mine = pile[viewport]
            // get the tail point
            const tail = mine[node]
            // and the head
            const head = mine[node + 1]
            // form their mid point
            const mid = tail.map((t, idx) => Math.trunc((t + head[idx]) / 2))
            // add it to the path
            mine.splice(node + 1, 0, mid)
            // return the new pile
            return pile
        })
        // all done
        return
    }

    // make a handler that displaces a collection of {nodes} by a given {delta}
    const displace = ({ nodes, delta }) => {
        // update the list
        setPixelPath(old => {
            // make a copy
            const pile = [...old]
            // and find the portion that corresponds to this {viewport}
            const mine = pile[viewport]

            // go through the node ids
            nodes.forEach(node => {
                // get each point
                const point = mine[node]
                // update it
                point[0] += delta.x
                point[1] += delta.y
                // and get the next one
                return
            })

            // and return the updated pile
            return pile
        })
        // all done
        return
    }

    // and return the handler
    return { add, split, displace }
}


// end of file
