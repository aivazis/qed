// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// local
// hooks
import { useDatasetShape } from '../../viz/useDatasetShape'
import { usePixelPathSelection } from '../../viz/usePixelPathSelection'
import { useSetPixelPath } from '../../viz/useSetPixelPath'


// a interactive entry with a coordinate of a point
export const Coordinate = ({ node, axis, point }) => {
    // make a handler that can update the {axis} coordinate of my {node}
    const { adjust } = useSetPixelPath()
    // and get the active dataset shape and origin
    const { origin, shape } = useDatasetShape()
    // the current point selection
    const selection = usePixelPathSelection()

    // deduce my state
    const selected = selection.has(node)

    // validate, clip and set the value
    const set = value => {
        // set up the bounds
        const min = origin[axis]
        const max = origin[axis] + shape[axis] - 1
        // if the value doesn't parse to a number
        if (isNaN(value)) {
            // set it to the minimum
            value = min
        }
        // if it's smaller than the minimum possible
        if (value < min) {
            // clip it
            value = min
        }
        // if it's larger than the maximum possible
        if (value > max) {
            // clip it
            value = max
        }
        // make the update
        adjust({ node, axis, value })
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
    font-size: 100%;
    width: 3.0rem;
    text-align: end;
    background-color: hsl(0deg, 0%, 7%);
    padding: 0.0rem 0.25rem 0.0rem 0.0rem;
    border: 0 transparent;
`

const Enabled = styled(Base)`
    & {
        color: hsl(0deg, 0%, 40%);
    }

    &:active{
        color: hsl(0deg, 0%, 60%);
    }

    &:focus{
        color: hsl(0deg, 0%, 60%);
    }

    &:invalid {
        color: hsl(0deg, 50%, 50%);
    }

    &::selection {
        color: hsl(0deg, 0%, 60%);
        background-color: hsl(0deg, 0%, 20%);
    }
`

const Selected = styled(Base)`
    color: hsl(28deg, 90%, 55%);
`


// end of file
