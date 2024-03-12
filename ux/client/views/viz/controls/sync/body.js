// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// locals
// hooks
import { useViews } from '../../../main/useViews'
// components
import { Dataset } from './dataset'
import { Channel } from './channel'
import { Offset } from './offset'
import { Path } from './path'
import { Scroll } from './scroll'
import { Zoom } from './zoom'

// the body of the sync control table
export const Body = () => {
    // get the set of views
    const { views } = useViews()
    // render
    return (
        <Container>
            {views.map(({ dataset }, viewport) => {
                // render
                return (
                    <Viewport key={`${dataset.name}:${viewport}`}>
                        <Dataset viewport={viewport}>{dataset.name}</Dataset>
                        <Channel viewport={viewport} />
                        <Zoom viewport={viewport} />
                        <Scroll viewport={viewport} />
                        <Path viewport={viewport} />
                        <Offset viewport={viewport} />
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