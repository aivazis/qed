// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// local
import { Cell } from './cell'
import { Toggle } from './toggle'

// the zoom sync control
export const Zoom = () => {
    // set aside some state
    const [state, setState] = React.useState(false)
    // build the state toggle
    const toggle = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // flip the state
        setState(old => !old)
        // all done
    }
    // render
    return (
        <Cell>
            <Toggle state={state} toggle={toggle} />
        </Cell>
    )
}


// end of file
