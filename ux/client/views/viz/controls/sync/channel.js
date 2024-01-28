// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
import { Cell } from './cell'
import { Toggle } from './toggle'

// the channel sync control
export const Channel = ({ state, toggle }) => {
    // render
    return (
        <Cell>
            <Toggle state={state} toggle={toggle} />
        </Cell>
    )
}


// end of file