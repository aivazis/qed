// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay'
import styled from 'styled-components'

// project
import { theme } from "~/palette"

// local
// hooks
import { useToggleClosedPath } from '~/views/viz/measure'
// components
import { Button } from './button'


// insert a point to the path after the given one
export const Close = ({ viewport, view }) => {
    // unpack the view
    const { measure } = useFragment(closeMeasureGetMeasureLayerFragment, view)
    // get the flag mutator
    const { toggle } = useToggleClosedPath(viewport)
    // get the current value of the flag
    const closed = measure.closed

    // assemble the behaviors
    const behaviors = {
        onClick: toggle,
    }

    // pick the representation based on the current state of the path
    const Toggle = closed ? Closed : Open

    // render
    return (
        <Button behaviors={behaviors}>
            <Toggle cx="500" cy="500" r="450" />
        </Button>
    )
}

const Closed = styled.circle`
    fill: ${props => theme.page.bright};
`

const Open = styled.circle`
    fill: none;

    stroke: ${props => theme.page.bright};
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`


// the fragment
const closeMeasureGetMeasureLayerFragment = graphql`
    fragment closeMeasureGetMeasureLayerFragment on View {
        measure {
            closed
        }
    }
`


// end of file
