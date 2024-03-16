// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
import { theme } from "~/palette"

// local
// hooks
import { useDatasetShape } from '../../../../main/useDatasetShape'
import { usePixelPathSelection } from '../../../../main/usePixelPathSelection'
import { useSetPixelPath } from '../../../../main/useSetPixelPath'


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
    font-size: 110%;
    width: 3.0rem;
    text-align: end;
    background-color: ${props => theme.page.background};
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


// end of file
