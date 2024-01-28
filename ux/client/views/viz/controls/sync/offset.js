// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// local
import { Cell } from './cell'
import { Coordinate } from './coordinate'
import { Toggle } from './toggle'

// the channel sync control
export const Scroll = ({ sync }) => {
    // set aside some state
    const [state, setState] = React.useState(sync)
    const [offset, setOffset] = React.useState([0, 0])
    // build the state toggle
    const toggle = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // flip the state
        setState(old => !old)
        // all done
        return
    }
    // build the state toggle
    const adjust = (axis, offset) => {
        console.log(axis, offset)
        // adjust the correct entry and set the state
        setOffset(old => old.toSpliced(axis, 1, offset))
        // all done
        return
    }
    // render
    return (
        <Housing>
            <Toggle state={state} toggle={toggle} />
            :
            <Coordinate point={offset} axis={0} adjust={adjust} />
            <Coordinate point={offset} axis={1} adjust={adjust} />
        </Housing>
    )
}

const Housing = styled(Cell)`
    min-width: 6em;
`

// end of file
