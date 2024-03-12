// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// project
// widgets
import { Tray } from '~/widgets'

// locals
// hooks
import { useMeasureLayer } from '../../../main/useMeasureLayer'
// components
import { Path } from './path'
import { Peek } from './peek'


// display the {measure} layer controls
export const Measure = () => {
    // get the {measure} layer status of the active {viewport}
    const measureLayer = useMeasureLayer()

    // if the {measure} layer has not been activated
    if (!measureLayer) {
        // nothing to show
        return null
    }

    // the platform dependent prompt; {platform} is deprecated, but the recommended replacement
    // is neither an approved standard nor widely implemented; the web...
    const stroke = navigator.platform.startsWith("Mac") ? "option+click" : "alt+click"

    // otherwise, render
    return (
        <Tray title="measure" state="enabled" initially={true} scale={0.5}>
            {/* display pixel values */}
            <Peek />
            {/* if the pixel path is empty, show a brief help message */}
            <Help>
                use {stroke} to pick points on the active view
            </Help>
            {/* render the pixel path */}
            <Path />
        </Tray>
    )
}


// the box with the hint about how to add points to the measure layer
const Help = styled.p`
    font-family: rubik-light;
    font-style: italic;
    margin: 0.0rem 1.0rem 0.5rem 1.0rem;
`


// end of file
