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
import { useAnchorPlace } from '~/views/viz/measure'


// a interactive entry with a coordinate of a point
export const Coordinate = ({ viewport, view, node, point, axis }) => {
    // unpack the view
    const { dataset, measure } = useFragment(coordinateMeasureGetMeasureLayerFragment, view)
    // make a handler that can update the {axis} coordinate of my {node}
    const { place } = useAnchorPlace(viewport)
    // get the active dataset shape and origin
    const { origin, shape } = dataset
    // and the selection
    const { selection } = measure

    // figure the state of this anchor
    const selected = selection.includes(node)

    // validate, clip and set the value
    const set = value => {
        // convert {axis} to an {index}
        const index = axis == "x" ? 1 : 0
        // set up the bounds
        const min = origin[index]
        const max = origin[index] + shape[index] - 1
        // if the value doesn't parse to a number
        if (isNaN(value)) {
            // set it to the minimum
            value = min
        }
        // clip the value
        value = Math.max(min, Math.min(value, max))
        // project to x and y
        const x = axis == "x" ? value : point.x
        const y = axis == "y" ? value : point.y
        // make the update
        place({ handle: node, position: { x, y } })
        // all done
        return
    }

    // on input
    const update = evt => {
        // get the new value
        const value = parseInt(evt.target.value)
        // and set it
        set(value)
        // all done
        return
    }

    // make a controller
    const behaviors = {
        // update on every keystroke; maybe disorienting
        // turn it off for now to see the effect across browsers
        // onInput: update,
        // commit the change to the value
        onChange: update,
    }

    // pick my entry based on my state
    const Entry = selected ? Selected : Enabled

    // make a mark
    return (
        <Entry type="text" value={point[axis]} {...behaviors} />
    )
}


// the base entry
const Base = styled.input`
    display: inline-block;
    appearance: textfield;
    outline: none;
    cursor: pointer;
    font-family: inconsolata;
    font-size: 110%;
    width: 3.0rem;
    text-align: end;
    background-color: ${props => theme.page.shaded};
    padding: 0.0rem 0.25rem 0.0rem 0.0rem;
    border: 0 transparent;
`

const Enabled = styled(Base)`
    & {
        color: ${() => theme.page.normal};
    }

    &:active{
        color: ${() => theme.page.bright};
    }

    &:focus{
        color: ${() => theme.page.bright};
    }

    &:invalid {
        color: ${() => theme.page.danger};
    }

    &::selection {
        color: ${() => theme.page.bright};
        background-color:${() => theme.page.selected};
    }
`

const Selected = styled(Base)`
    color: ${() => theme.page.highlight};
`


// the fragment
const coordinateMeasureGetMeasureLayerFragment = graphql`
    fragment coordinateMeasureGetMeasureLayerFragment on View {
        dataset {
            origin
            shape
        }
        measure {
            selection
        }
    }
`


// end of file
