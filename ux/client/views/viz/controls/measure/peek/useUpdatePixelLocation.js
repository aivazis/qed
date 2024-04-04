// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import { fetchQuery, useRelayEnvironment } from 'react-relay'

// local
// context
import { Context } from './context'
// hooks
import { pixelValueQuery } from './useGetPixelValue'

// the code below looks tricky because it is trying to avoid suspending component rendering
// while the query is in flight and rendering again once the result is available because this
// causes flicker

// build handlers that update the pixel location
export const useUpdatePixelLocation = view => {
    // get the current relay environment
    const environment = useRelayEnvironment()
    // unpack the view
    const { dataset, zoom, measure } = useFragment(
        useUpdatePixelLocationMeasureGetPixelLocationFragment, view
    )
    // pull info out of my context
    const {
        // query state and info management
        loading, variables, setLoading, setVariables, setOptions,
    } = React.useContext(Context)

    // unpack the dataset
    const { origin, shape } = dataset
    // unpack the measure layer info
    const { path: pixelPath, selection } = measure

    // build the handler that refreshes the query
    const refresh = ({ x, y }) => {
        // if the query is in flight
        if (loading) {
            // bail
            return
        }
        // otherwise, mark this query as in-flight
        setLoading(true)

        // assemble the query variables
        const queryVars = { ...variables, line: y, sample: x }
        // {fetchQuery} will update the {relay} store; this ensures that when {peek}
        // renders again, all the necessary data is already in place, and the rendering
        // will not suspend
        fetchQuery(environment, pixelValueQuery, queryVars)
            .subscribe({
                // once done
                complete: () => {
                    // the query is no longer in flight
                    setLoading(false)
                    // adjust the variables
                    setVariables(queryVars)
                    // adjust the options
                    setOptions(old => ({
                        // transaction id
                        fetchKey: (old?.fetchKey ?? 0) + 1,
                        // force {relay} to resolve the query without bothering
                        // the server any more
                        fetchPolicy: 'store-only',
                    }))
                },
                // if something goes wrong
                error: () => {
                    // clear the flag
                    setLoading(false)
                    // and bail
                    return
                }
            })
        // all done
        return
    }

    // build a handler that adjust the current values of the variables and refreshes
    const nudge = ({ dx, dy }) => {
        // compute the new location
        const x = variables.sample + dx
        const y = variables.line + dy
        // refresh
        refresh({ x, y })
        // all done
        return
    }

    // build a handler that extracts a pixel location of interest either from the current
    // mouse location in the active view, or the select mark in the measure layer
    const track = evt => {
        // if the selection is not empty
        if (selection.length > 0) {
            // decouple from the mouse; instead, get the index of the selected mark
            const mark = [...selection][0]
            // get the associated point
            const point = pixelPath[mark]
            // and use it as the query location
            refresh({ y: point.y, x: point.x })
            // all done
            return
        }

        // turn the zoom level into a scale
        const scale = [2 ** -zoom.vertical, 2 ** -zoom.horizontal]
        // get the viewport
        // make sure to grab the viewport, not whatever the mouse is over
        const element = evt.currentTarget
        // measure it
        const box = element.getBoundingClientRect()
        // compute the location of the mouse relative to the viewport
        // and take the zoom level into account
        const x = Math.trunc(scale[1] * (element.scrollLeft + evt.clientX - box.left))
        const y = Math.trunc(scale[0] * (element.scrollTop + evt.clientY - box.top))

        // if the position overflows the dataset along the x-axis
        if (x < origin[1] || x > origin[1] + shape[1]) {
            // bail
            return
        }
        // repeat for the y axis
        if (y < origin[0] || y > origin[0] + shape[0]) {
            // bail
            return
        }

        // record the current mouse location; this triggers the {sample} query to refresh
        refresh({ x, y })

        // all done
        return
    }

    // and return the pixel data and the location tracker
    return { nudge, refresh, track }
}


// the fragment
const useUpdatePixelLocationMeasureGetPixelLocationFragment = graphql`
    fragment useUpdatePixelLocationMeasureGetPixelLocationFragment on View {
        dataset {
            origin
            shape
        }
        zoom {
            horizontal
            vertical
        }
        measure {
            path {
                x
                y
            }
            selection
        }
    }
`


// end of file
