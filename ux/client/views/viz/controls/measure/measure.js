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


//  display the {measure} layers controls
export const Measure = () => {
    // get the active viewport

    // get the {measure} layer status
    const measureLayer = useMeasureLayer()
    // and the set of pixels on the path
    const pixelPath = usePixelPath()

    // if the {measure} layer has not been activated
    if (!measureLayer) {
        // noting to show
        return null
    }

    // render
    return (
        <Tray title="measure" state="enabled" initially={true}>
            {pixelPath.length === 0 &&
                <Help>
                    Pick points using Alt+Click.
                    On a Mac, the key may be labeled "option", or &#8997;
                </Help>
            }
        </Tray>
    )
}


// part
const Help = styled.p`
    font-family: rubik-light;
    font-size: 75%;
    padding: 1rem;

`


// end of file
