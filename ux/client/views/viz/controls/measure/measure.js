// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// project
// widgets
import { Tray } from '~/widgets'

// locals
// context
import { Provider } from './context'
// hooks
import { useMeasureLayer } from '../../viz/useMeasureLayer'
import { usePixelPath } from '../../viz/usePixelPath'
// components
import { Minimap } from './minimap'
import { Path } from './path'


// set up the context
export const Measure = (props) => {
    // set up my context and embed my panel
    return (
        <Provider>
            <Panel {...props} />
        </Provider>
    )
}


// display the {measure} layer controls
const Panel = () => {
    // get the {measure} layer status of the active {viewport}
    const measureLayer = useMeasureLayer()
    // and the set of pixels on its profile path
    const pixelPath = usePixelPath()

    // if the {measure} layer has not been activated
    if (!measureLayer) {
        // nothing to show
        return null
    }

    // otherwise, render
    return (
        <Tray title="measure" state="enabled" initially={true}>
            {/* if the pixel path is empty, show a brief help message */}
            {pixelPath.length === 0 &&
                <Help>
                    Pick points using Alt+Click.
                    On a Mac, the key may be labeled "option", or &#8997;
                </Help>
            }
            {/* render the pixel path */}
            <Path path={pixelPath} />
            {/* and the mini map */}
            <Minimap path={pixelPath} />
        </Tray>
    )
}


// part
const Help = styled.p`
    font-family: rubik-light;
    font-size: 75%;
    padding: 1.0rem;
`


// end of file
