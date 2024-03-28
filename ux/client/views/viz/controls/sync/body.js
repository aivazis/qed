// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// locals
// components
import { Dataset } from './dataset'
import { Channel } from './channel'
import { Offset } from './offset'
import { Path } from './path'
import { Scroll } from './scroll'
import { Zoom } from './zoom'

// the body of the sync control table
export const Body = ({ qed, mark }) => {
    // MGA: FIXME
    console.group(`views.viz.viz.controls.sync.body: FIREWALL`)
    console.log(` -*- NEEDS FRAGMENT TO EXTRACT dataset -*-`)
    console.groupEnd()
    // get the set of views; NEEDS FRAGMENT
    const { views } = qed

    // render
    return (
        <Container>
            {views.map(({ dataset }, viewport) => {
                // render
                return (
                    <Viewport key={`${dataset.name}:${viewport}`}>
                        <Dataset viewport={viewport}>{dataset.name}</Dataset>
                        <Channel viewport={viewport} mark={mark} />
                        <Zoom viewport={viewport} mark={mark} />
                        <Scroll viewport={viewport} mark={mark} />
                        <Path viewport={viewport} mark={mark} />
                        <Offset viewport={viewport} mark={mark} />
                    </Viewport>
                )
            })}
        </Container>
    )
}


// the table body
const Container = styled.tbody`
    font-size: 100%;
`

// viewport info
const Viewport = styled.tr`
    cursor: default;
    vertical-align: middle;
`


// end of file