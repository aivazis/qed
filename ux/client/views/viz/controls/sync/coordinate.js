// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// an interactive entry with a pixel offset
export const Coordinate = ({ className, point, axis, adjust }) => {
    // state
    const selected = false
    // on input
    const update = evt => {
        // get the new value
        const coord = parseInt(evt.target.value)
        // if the conversion fails
        if (isNaN(coord)) {
            // bail
            return
        }
        // and set it
        adjust({ ...point, [axis]: coord })
        // all done
        return
    }
    // assemble my behaviors
    const behaviors = {
        // value update
        onChange: update,
    }

    // unpack my value
    const offset = point[axis]
    // render it
    // const rep = `${offset >= 0 ? "+" : ""}${offset}`
    const rep = `${offset}`

    // pick my entry based on my state
    const Entry = selected ? Selected : Enabled

    // make a mark
    return (
        <Entry className={className} type="text" value={rep} {...behaviors} />
    )
}


// the base entry
const Base = styled.input`
    display: inline-block;
    appearance: textfield;
    outline: none;
    cursor: pointer;
    width: 4.0em;
    background-color: hsl(0deg, 0%, 7%);
    padding: 0.0rem;
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
