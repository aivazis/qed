// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context, pixelPathDefault } from './context'
import { useSetPixelPathSelection } from './useSetPixelPathSelection'
import { useDatasetShape } from './useDatasetShape'


// access to the mutator of the list of profile points
export const useSetPixelPath = (viewport = null) => {
    // get the flag mutator
    const { activeViewport, setPixelPath } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport
    // make a handler that clears the selection to use when removing a point from the path
    const { clear: clearSelection } = useSetPixelPathSelection(viewport)
    // and get the active dataset shape and origin
    const { origin, shape } = useDatasetShape(viewport)


    // make a handler that clears the current selection
    const clear = () => {
        // reset the selection to an empty set
        setPixelPath(old => {
            // make a copy
            const paths = [...old]
            // clear out the one that corresponds to {viewport}
            paths[viewport] = pixelPathDefault()
            // and return the new pile
            return paths
        })
        // all done
        return
    }

    // make a handler that adds a point to the pile
    // the optional {pos} adds the point {p} before the supplied position, otherwise the point is
    // pushed to the end
    const add = (p, pos = null) => {
        // update the list
        setPixelPath(old => {
            // make a copy of the whole pile
            const pile = [...old]
            // get the portion that corresponds to this {viewport}
            const mine = pile[viewport].points
            // add the new point to it
            pos === null ? mine.push(p) : mine.splice(pos, 0, p)
            // and return the new pile
            return pile
        })
        // all done
        return
    }

    // make a handler that removes a point from the pile
    const remove = node => {
        // update the list
        setPixelPath(old => {
            // clear the selection; removing a point scrambles the node indices...
            clearSelection(node)
            // make a copy of the whole pile
            const pile = [...old]
            // get the portion that corresponds to this {viewport}
            const mine = pile[viewport].points
            // remove the point at the given slot
            mine.splice(node, 1)
            // and return the new pile
            return pile
        })
        // all done
        return
    }

    // make a handler that adds a point to the path by splitting an existing leg in two
    // don't call this before making sure that both {node} and {node+1} are in the path
    const split = node => {
        // update the list
        setPixelPath(old => {
            // make a copy
            const pile = [...old]
            // and find the portion that corresponds to this {viewport}
            const mine = pile[viewport].points
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

    // adjust a coordinate of a single point
    const adjust = ({ node, axis, value }) => {
        // update the list
        setPixelPath(old => {
            // make a copy
            const pile = [...old]
            // and find the portion that corresponds to this {viewport}
            const mine = pile[viewport].points
            // make the adjustment
            mine[node][axis] = Math.max(origin[axis], Math.min(shape[axis], value))
            // and return the updated points
            return pile
        })
        // all done
        return
    }

    // nudge a coordinate of a single {node} by a given {value} along a specified {axis}
    const nudge = ({ node, axis, value = 1 }) => {
        // update the list
        setPixelPath(old => {
            // make a copy
            const pile = [...old]
            // and find the portion that corresponds to this {viewport}
            const mine = pile[viewport].points
            // make the adjustment
            mine[node][axis] = Math.max(origin[axis],
                Math.min(shape[axis], mine[node][axis] + value))
            // and return the updated points
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
            const mine = pile[viewport].points

            // go through the node ids
            nodes.forEach(node => {
                // get each point
                const point = mine[node]
                // clip and update
                point[0] = Math.max(origin[0], Math.min(shape[0], point[0] + delta.y))
                point[1] = Math.max(origin[1], Math.min(shape[1], point[1] + delta.x))
                // and get the next one
                return
            })

            // and return the updated pile
            return pile
        })
        // all done
        return
    }

    // make a handler that toggles whether the path is open or closed
    const toggle = () => {
        // update the list
        setPixelPath(old => {
            // make a copy of the whole pile
            const pile = [...old]
            // get the portion that corresponds to this {viewport}
            const mine = pile[viewport]
            // toggle the closed flags
            mine.closed = !mine.closed
            // and return the new pile
            return pile
        })
        // all done
        return
    }

    // and return the handlers
    return { clear, add, adjust, displace, nudge, remove, split, toggle }
}


// end of file
