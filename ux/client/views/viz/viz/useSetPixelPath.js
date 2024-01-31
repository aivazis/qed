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
import { useSynced } from './useSynced'


// access to the mutator of the list of profile points
export const useSetPixelPath = (viewport = null) => {
    // get the flag mutator
    const { views, activeViewport, setPixelPath } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport
    // make a handler that clears the selection to use when removing a point from the path
    const { clear: clearSelection } = useSetPixelPathSelection(viewport)
    // and get the active dataset shape and origin
    const { origin, shape } = useDatasetShape(viewport)
    // get the sync table
    const synced = useSynced()

    // make a handler that clears the current selection
    const clear = () => {
        // reset the selection to an empty set
        setPixelPath(old => {
            // make a copy
            const paths = [...old]
            // clear out the one that corresponds to {viewport}
            paths[viewport] = pixelPathDefault()
            // if i'm path synced
            if (synced[viewport].path) {
                // go through the table
                synced.forEach((entry, port) => {
                    // if this is my entry
                    if (port === viewport) {
                        // leave me alone
                        return
                    }
                    // if this viewport is not path synced
                    if (!entry.path) {
                        // leave it alone
                        return
                    }
                    // otherwise, clear its path as well
                    paths[port] = pixelPathDefault()
                    // all done
                    return
                })
            }
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
            // if i'm path synced
            if (synced[viewport].path) {
                // go through the table
                synced.forEach((entry, port) => {
                    // if this is my entry
                    if (port === viewport) {
                        // leave me alone
                        return
                    }
                    // if this viewport is not path synced
                    if (!entry.path) {
                        // leave it alone
                        return
                    }
                    // otherwise, get the path of this viewport
                    const theirs = pile[port].points
                    // make a copy of the point
                    const clone = [...p]
                    // and add the new point
                    pos === null ? theirs.push(clone) : theirs.splice(pos, 0, clone)
                    // all done
                    return
                })
            }
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
            clearSelection()
            // make a copy of the whole pile
            const pile = [...old]
            // get the portion that corresponds to this {viewport}
            const mine = pile[viewport].points
            // remove the point at the given slot
            mine.splice(node, 1)
            // if i'm path synced
            if (synced[viewport].path) {
                // go through the table
                synced.forEach((entry, port) => {
                    // if this is my entry
                    if (port === viewport) {
                        // leave me alone
                        return
                    }
                    // if this viewport is not path synced
                    if (!entry.path) {
                        // leave it alone
                        return
                    }
                    // otherwise, get the path of this viewport
                    const theirs = pile[port].points
                    // remove the point at the given slot
                    theirs.splice(node, 1)
                    // all done
                    return
                })
            }
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
            // if i'm path synced
            if (synced[viewport].path) {
                // go through the table
                synced.forEach((entry, port) => {
                    // if this is my entry
                    if (port === viewport) {
                        // leave me alone
                        return
                    }
                    // if this viewport is not path synced
                    if (!entry.path) {
                        // leave it alone
                        return
                    }
                    // otherwise, get the path of this viewport
                    const theirs = pile[port].points
                    // get the tail point
                    const tail = theirs[node]
                    // and the head
                    const head = theirs[node + 1]
                    // form their mid point
                    const mid = tail.map((t, idx) => Math.trunc((t + head[idx]) / 2))
                    // add it to the path
                    theirs.splice(node + 1, 0, mid)
                    // all done
                    return
                })
            }
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
            // if i'm path synced
            if (synced[viewport].path) {
                // go through the table
                synced.forEach((entry, port) => {
                    // if this is my entry
                    if (port === viewport) {
                        // leave me alone
                        return
                    }
                    // if this viewport is not path synced
                    if (!entry.path) {
                        // leave it alone
                        return
                    }
                    // otherwise, get the path of this viewport
                    const theirs = pile[port].points
                    // and the origin and shape of its dataset
                    const { origin, shape } = views[port].dataset
                    // make the adjustment
                    theirs[node][axis] = Math.max(origin[axis], Math.min(shape[axis], value))
                    // all done
                    return
                })
            }
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
            mine[node][axis] = Math.max(
                origin[axis], Math.min(shape[axis], mine[node][axis] + value)
            )
            // if i'm path synced
            if (synced[viewport].path) {
                // go through the table
                synced.forEach((entry, port) => {
                    // if this is my entry
                    if (port === viewport) {
                        // leave me alone
                        return
                    }
                    // if this viewport is not path synced
                    if (!entry.path) {
                        // leave it alone
                        return
                    }
                    // otherwise, get the path of this viewport
                    const theirs = pile[port].points
                    // and the origin and shape of its dataset
                    const { origin, shape } = views[port].dataset
                    // make the adjustment
                    theirs[node][axis] = Math.max(
                        origin[axis], Math.min(shape[axis], theirs[node][axis] + value)
                    )
                    // all done
                    return
                })
            }
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
            // if i'm path synced
            if (synced[viewport].path) {
                // go through the table
                synced.forEach((entry, port) => {
                    // if this is my entry
                    if (port === viewport) {
                        // leave me alone
                        return
                    }
                    // if this viewport is not path synced
                    if (!entry.path) {
                        // leave it alone
                        return
                    }
                    // otherwise, get the path of this viewport
                    const theirs = pile[port].points
                    // and the origin and shape of its dataset
                    const { origin, shape } = views[port].dataset
                    // go through the node ids
                    nodes.forEach(node => {
                        // get each point
                        const point = theirs[node]
                        // clip and update
                        point[0] = Math.max(origin[0], Math.min(shape[0], point[0] + delta.y))
                        point[1] = Math.max(origin[1], Math.min(shape[1], point[1] + delta.x))
                        // and get the next one
                        return
                    })
                    // all done
                    return
                })
            }

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
            // if i'm path synced
            if (synced[viewport].path) {
                // go through the table
                synced.forEach((entry, port) => {
                    // if this is my entry
                    if (port === viewport) {
                        // leave me alone
                        return
                    }
                    // if this viewport is not path synced
                    if (!entry.path) {
                        // leave it alone
                        return
                    }
                    // get the portion that corresponds to this {port}
                    const theirs = pile[port]
                    // set the closed flags
                    theirs.closed = mine.closed
                    // all done
                    return
                })
            }
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
