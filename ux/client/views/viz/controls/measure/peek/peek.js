// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// locals
// context
import { Provider } from './context'
// hooks
import { useViewports } from '~/views/viz'
import { useGetPixelValue } from './useGetPixelValue'
import { useUpdatePixelLocation } from './useUpdatePixelLocation'
// components
import { Channel } from './channel'
import { Minimap } from './minimap'


// N.B.:
// displaying the dataset value under the current cursor position involves
//   - installing an event listener in the active viewport so we can track the mouse
//   - transforming the mouse coordinates to dataset coordinate system
//   - issuing a query to have the server look up the value
//   - rendering the result


// display the pixel value at a location
export const Peek = (props) => {
    // set up my context and embed my panel
    return (
        <Provider {...props}>
            <Panel {...props} />
        </Provider>
    )
}


// the panel implementation
const Panel = ({ view }) => {
    // get the viewport registry
    const { activeViewport, viewports } = useViewports()
    // get the pixel value
    const { sample } = useGetPixelValue()
    // and the tracker
    const { track } = useUpdatePixelLocation(view)

    // the query refresh that's invoked when the mouse moves to a new pixel
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

    // sometimes, i'm asked to refresh but there is no data
    if (!sample) {
        // bail
        return null
    }
    // unpack
    const { pixel, value } = sample

    // render
    return (
        <Box>
            {/* the table header with the cursor location */}
            <Header>
                {/* the label */}
                <Title>peek</Title>
            </Header>
            {/* the reps */}
            {value.map(({ channel, reps }) => (
                <Channel key={channel} channel={channel} reps={reps} />
            ))}
            {/* draw the minimap */}
            <Minimap viewport={activeViewport} view={view} point={pixel} />
        </Box>
    )
}


// the container
const Box = styled.div`
    margin: 0.5rem 1.0rem 0.5rem 1.0rem;
`

const Header = styled.div`
`

const Title = styled.span`
    display: inline-block;
    font-family: rubik-light;
    width: 2.5rem;
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    margin: 0.0rem 0.0rem 0.1rem 0.0rem;
    cursor: default;
    color: ${() => theme.page.bright};
`


// end of file
