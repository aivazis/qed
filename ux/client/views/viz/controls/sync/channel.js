// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// local
import { Toggle } from './toggle'

// the channel sync control
export const Channel = () => {
    // render
    return (
        <Cell>
            <Toggle size={8} />
        </Cell>
    )
}


// cells
const Cell = styled.td`
    padding: 0.125rem;
    text-align: center;
    vertical-align: bottom;
`

// end of file
