// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import { graphql, useLazyLoadQuery, fetchQuery, useRelayEnvironment } from 'react-relay'
import styled from 'styled-components'


// locals
// hooks
import { useDatasetShape } from '../../viz/useDatasetShape'
import { useGetZoomLevel } from '../../viz/useGetZoomLevel'
import { useViewports } from '../../viz/useViewports'
// components
import { Channel } from './channel'
import { Minimap } from './minimap'


// N.B.:
// displaying the dataset value under the current cursor position involves
//   - installing an event listener in the active viewport so we can track the mouse
//   - transforming the mouse coordinates to dataset coordinate system
//   - issuing a query to have the server look up the value
//   - rendering the result

// the code below looks tricky because it is trying to avoid suspending component rendering
// while the query is in flight and rendering again once the result is available because this
// causes flicker


// display the {measure} layer controls
export const Track = () => {
    // get the viewport registry
    const { activeViewport, viewports } = useViewports()
    // get the zoom level of the active viewport
    const zoom = useGetZoomLevel()
    // and the extent of its dataset
    const { name, origin, shape } = useDatasetShape()

    // query state management
    const [loading, setLoading] = React.useState(false)
    // query payload
    const [payload, setPayload] = React.useState({
        options: null,
        variables: { dataset: name, line: origin[0], sample: origin[1] }
    })

    // get the environment
    const environment = useRelayEnvironment()
    // get the data
    const { sample } = useLazyLoadQuery(query, payload.variables, payload.options)

    // make a handler that tracks the mouse location in data coordinates
    const track = evt => {
        // turn the zoom level into a scale
        const scale = 2 ** zoom

        // get the viewport
        // make sure to grab the viewport, not whatever the mouse is over
        const element = evt.currentTarget
        // measure it
        const box = element.getBoundingClientRect()
        // compute the location of the mouse relative to the viewport
        // and take the zoom level into account
        const x = Math.trunc(scale * (element.scrollLeft + evt.clientX - box.left))
        const y = Math.trunc(scale * (element.scrollTop + evt.clientY - box.top))

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
        refresh({ line: y, sample: x })

        // all done
        return
    }

    // the query refresh that's invoked when the mouse moves to a new pixel
    const refresh = (variables) => {
        // if the query is in flight
        if (loading) {
            // bail
            return
        }
        // otherwise, mark this query as in-flight
        setLoading(true)

        // assembled the query variables
        const queryVars = { ...payload.variables, ...variables, }
        // {fetchQuery} will update the {relay} store; this ensures that when {track}
        // renders again, all the necessary data is already in place, and the rendering
        // will not suspend
        fetchQuery(environment, query, queryVars)
            .subscribe({
                // once done
                complete: () => {
                    // the query is no longer in flight
                    setLoading(false)
                    // so adjust the {relay} fetch policy to only look in the store
                    setPayload(old => ({
                        // populate the query options
                        options: {
                            // transaction id
                            fetchKey: (old.options?.fetchKey ?? 0) + 1,
                            // don't bother the server
                            fetchPolicy: 'store-only',
                        },
                        // update the search parameters with the new mouse coordinates
                        variables: queryVars,
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

    // install a tracker on the active viewport
    React.useEffect(() => {
        // get the active viewport ref
        const target = viewports[activeViewport]
        // install the tracker
        target.addEventListener("mousemove", track)
        // make an abort controller
        const controller = new AbortController()
        // and register a clean up
        return () => {
            // that removes the listeners
            target.removeEventListener("mousemove", track)
            // and aborts any pending requests
            controller.abort()
            // all done
            return
        }
    })

    // unpack
    const { pixel, value } = sample

    // render
    return (
        <Box>
            {/* the table header with the cursor location */}
            <Header>
                {/* the label */}
                <Title>peek</Title>
                {/* the mouse coordinates */}
                <Coordinate>{pixel[0]}</Coordinate>
                x
                <Coordinate>{pixel[1]}</Coordinate>
            </Header>
            {/* the reps */}
            {value.map(({ channel, reps }) => (
                <Channel key={channel} channel={channel} reps={reps} />
            ))}
            {/* draw the minimap */}
            <Minimap point={pixel} />
        </Box>
    )
}


// the container
const Box = styled.div`
    margin: 0.5rem 1.0rem 0.5rem 1.0rem;
`

const Header = styled.div`
    font-size: 65%;
`

const Title = styled.span`
    display: inline-block;
    font-family: rubik-light;
    width: 2.5rem;
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    margin: 0.0rem 0.0rem 0.1rem 0.0rem;
    color: hsl(0deg, 0%, 75%);
`

const Coordinate = styled.span`
    font-family: inconsolata;
    cursor: default;
    padding: 0.0rem 0.25rem;
`

// the query
const query = graphql`
    query track_sampleDatasetQuery($dataset: ID!, $line: Int!, $sample: Int!) {
        sample(dataset: $dataset, line: $line, sample: $sample){
            pixel
            value {
                channel
                reps {
                    rep
                    units
                }
            }
        }
    }
`


// end of file
