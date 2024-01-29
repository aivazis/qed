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

// the channel sync control
export const Offset = ({ offset, update }) => {
    // build the state toggle
    const adjust = (axis, value) => {
        // cast the value to an int
        const coord = parseInt(value)
        // if this fails
        if (isNaN(coord)) {
            // bail
            return
        }
        // adjust the correct entry and set the state
        update({ ...offset, [axis]: coord })
        // all done
        return
    }
    // render
    return (
        <Housing>
            <Line point={offset} axis={"y"} adjust={adjust} />
            <Sample point={offset} axis={"x"} adjust={adjust} />
        </Housing>
    )
}

const Housing = styled(Cell)`
    min-width: 6em;
`

const Line = styled(Coordinate)`
    text-align: right;
    padding-right: 0.5em;
`

const Sample = styled(Coordinate)`
    text-align: left;
    padding-left: 0.5em;
`

// end of file
