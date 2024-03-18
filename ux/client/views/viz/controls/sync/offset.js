// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// local
// hooks
import { useSynced } from '../../../main/useSynced'
import { useSyncAspect } from '../../../main/useSyncAspect'
// components
import { Cell } from './cell'
import { Coordinate } from './coordinate'


// the channel sync control
export const Offset = ({ viewport, mark }) => {
    // get the sync state of all the viewports
    const synced = useSynced()
    // get the sync handler factory
    const { update } = useSyncAspect()

    // get the offset
    const offset = synced[viewport].offset
    // build the handler
    const adjust = () => {
        // mark
        mark()
        // update
        update(viewport, "offset")
        // and done
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
    font-family: inconsolata;
    font-size: 110%;
    width: 9.5em;
    min-width: 9.5em;
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
