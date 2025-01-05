// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from '~/palette'


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
    background-color: ${() => theme.page.shaded};
    padding: 0.0rem;
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
        background-color: ${() => theme.page.selected}
    }
`

const Selected = styled(Base)`
    color: ${() => theme.page.highlight};
`


// end of file
