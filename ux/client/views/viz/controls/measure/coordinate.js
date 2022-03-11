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
import { useSetPixelPath } from '../../viz/useSetPixelPath'


// a interactive entry with a coordinate of a point
export const Coordinate = ({ node, axis, point }) => {
    // make a ref for my input field
    const input = React.useRef()
    // make me handler that can update the {axis} coordinate of my {node}
    const { adjust } = useSetPixelPath()
    // and get the active dataset shape and origin
    const { origin, shape } = useDatasetShape()

    // validate, clip and set the value
    const set = value => {
        // if the value doesn't parse to a number
        if (isNaN(value)) {
            // set it to the minimum
            value = origin[axis]
        }
        // if it's smaller than the minimum possible
        if (value < origin[axis]) {
            // clip it
            value = origin[axis]
        }
        // if it's larger than the maximum possible
        if (value > shape[axis]) {
            // clip it
            value = shape[axis]
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

    // make a mark
    return (
        <Entry ref={input} type="text" value={point[axis]} {...behaviors} />
    )
}


const Entry = styled.input`
    & {
        display: inline-block;
        appearance: textfield;
        outline: none;
        font-family: inconsolata;
        font-size: 100%;
        width: 3.0rem;
        text-align: end;
        color: hsl(0deg, 0%, 40%);
        background-color: hsl(0deg, 0%, 7%);
        padding: 0.0rem 0.25rem 0.0rem 0.0rem;
        border: 0 transparent;
    }

    &:active{
        color: hsl(28deg, 90%, 55%);
    }

    &:focus{
        color: hsl(28deg, 90%, 55%);
    }

    &:invalid {
        color: hsl(0deg, 50%, 50%);
    }

    &::selection{
        color: hsl(28deg, 90%, 55%);
        background-color: hsl(0deg, 0%, 20%);
    }
`

// end of file
