// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// local
// hooks
import { useSyncUpdateOffset } from './useSyncUpdateOffset'
// components
import { Cell } from './cell'
import { Coordinate } from './coordinate'


// the channel sync control
export const Offset = ({ viewport, view, mark }) => {
    // unpack the view
    const { sync } = useFragment(offsetSyncTableFragment, view)
    // build the single viewport update
    const { update } = useSyncUpdateOffset()

    // get the offset
    const offset = sync.offsets
    // build the handler
    const adjust = offset => {
        // mark
        mark()
        // update
        update({ viewport, offset })
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

const offsetSyncTableFragment = graphql`
    fragment offsetSyncTableFragment on View {
        sync {
            offsets {x y}
        }
    }
`


// end of file
