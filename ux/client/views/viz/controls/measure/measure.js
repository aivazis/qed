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
// hooks
import { useMeasureLayer } from '../../viz/useMeasureLayer'
import { usePixelPath } from '../../viz/usePixelPath'
// components
import { Actions } from './actions'
import { Minimap } from './minimap'
import { Path } from './path'
import { Track } from './track'


// display the {measure} layer controls
export const Measure = () => {
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
            {/* track the mouse */}
            <Track />
            {/* if the pixel path is empty, show a brief help message */}
            {pixelPath.length === 0 &&
                <Help>
                    Pick points using Alt+Click.
                    On a Mac, the key may be labeled "option", or &#8997;
                </Help>
            }
            {/* render the pixel path */}
            <Path />
            {/* the mini map */}
            <Minimap />
            {/* and the actions */}
            <Actions />
        </Tray>
    )
}


// the box with the hint about how to add points to the measure layer
const Help = styled.p`
    font-family: rubik-light;
    font-size: 75%;
    margin: 0.0rem 1.0rem 1.0rem 1.0rem;
`


// end of file
