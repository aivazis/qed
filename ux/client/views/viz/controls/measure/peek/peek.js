// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// locals
// context
import { Provider } from './context'
// hooks
import { useGetPixelValue } from './useGetPixelValue'
import { useUpdatePixelLocation } from './useUpdatePixelLocation'
import { useViewports } from '../../../viz/useViewports'
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
        <Provider>
            <Panel {...props} />
        </Provider>
    )
}


// the panel implementation
const Panel = () => {
    // get the viewport registry
    const { activeViewport, viewports } = useViewports()
    // get the pixel value
    const sample = useGetPixelValue()
    // and the tracker
    const { track } = useUpdatePixelLocation()

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
    cursor: default;
    color: hsl(0deg, 0%, 75%);
`

const Coordinate = styled.span`
    font-family: inconsolata;
    cursor: default;
    padding: 0.0rem 0.25rem;
`


// end of file
