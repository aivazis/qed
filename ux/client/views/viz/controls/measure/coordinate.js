// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// hooks
import { useEvent } from '~/hooks'

// local
// hooks
import { useSetPixelPath } from '../../viz/useSetPixelPath'
import { useViews } from '../../viz/useViews'


// a interactive entry with a coordinate of a point
export const Coordinate = ({ node, axis, point }) => {
    // make a ref for my input field
    const input = React.useRef()
    // get the {activeViewport} and the set of {views} from {viz}
    const { views, activeViewport } = useViews()
    // make me handler that can update the {axis} coordinate of my {node}
    const { adjust } = useSetPixelPath()

    // get the {dataset} in the active view
    const { dataset } = views[activeViewport]
    // and unpack its shape and it origin
    const { origin, shape } = dataset

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

    // install some event listeners
    // when the input field changes values
    useEvent({
        name: "input", listener: update, client: input,
    })
    // when the input field loses focus
    useEvent({
        name: "change", listener: update, client: input,
    })

    // make a mark
    return (
        <Entry ref={input} type="text" value={point[axis]} />
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
