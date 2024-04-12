// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay'
import styled from 'styled-components'

// project
// widgets
import { Spacer, Tray } from '~/widgets'
// colors
import { theme } from "~/palette"

// locals
// hooks
import { useReset } from './useReset'
// components
import { Path } from './path'
import { Peek } from './peek'
import { Reset } from './reset'
import { Save } from './save'


// display the {measure} layer controls
export const Measure = ({ viewport, view }) => {
    // get the {measure} layer status of the active {viewport}
    const { measure } = useFragment(measureControlsGetMeasureLayerStateFragment, view)
    // make a handler that resets the state to the persisted defaults
    const { reset: restoreDefaults } = useReset(viewport)
    // if the {measure} layer has not been activated
    if (!measure.active) {
        // nothing to show
        return null
    }

    // setup the reset action
    const reset = () => {
        // restore the default
        restoreDefaults()
        // all done
        return
    }

    // the platform dependent prompt; {platform} is deprecated, but the recommended replacement
    // is neither an approved standard nor widely implemented; the web...
    const stroke = navigator.platform.startsWith("Mac") ? "option+click" : "alt+click"

    // otherwise, render
    return (
        <Tray title="measure" state="enabled" initially={true} scale={0.5}>
            <Header>
                <Spacer />
                <Save save={reset} enabled={false} />
                <Reset reset={reset} enabled={measure.dirty} />
            </Header>
            {/* display pixel values */}
            <Peek view={view} />
            {/* if the pixel path is empty, show a brief help message */}
            <Help>
                use {stroke} to pick points on the active view
            </Help>
            {/* render the pixel path */}
            <Path view={view} />
        </Tray>
    )
}


// the section header
const Header = styled.div`
    height: 1.5rem;
    margin: 0.5rem 0.0rem 0.25rem 1.0rem;
    // for my children
    display: flex;
    flex-direction: row;
    align-items: center;
`

// the box with the hint about how to add points to the measure layer
const Help = styled.p`
    font-family: rubik-light;
    font-size: 110%;
    font-style: italic;
    margin: 0.0rem 1.0rem 0.5rem 1.0rem;
    color: ${() => theme.page.normal}
`


// the fragment
const measureControlsGetMeasureLayerStateFragment = graphql`
    fragment measureControlsGetMeasureLayerStateFragment on View {
        measure {
            dirty
            active
        }
    }
`


// end of file
