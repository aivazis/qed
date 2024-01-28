// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// locals
// hooks
import { useViews } from '../../viz/useViews'
import { useSynced } from '../../viz/useSynced'
import { useToggleSyncedAspect, useSetSyncedAspect } from '../../viz/useSyncAspect'
// components
import { Cell } from './cell'
import { Channel } from './channel'
import { Path } from './path'
import { Scroll } from './scroll'
import { Zoom } from './zoom'

// the body of the sync control table
export const Body = () => {
    // get the set of views
    const { views } = useViews()
    // get the sync state of all the viewports
    const synced = useSynced()
    // build the toggle factory
    const toggle = useToggleSyncedAspect()
    // and the setter factory
    const set = useSetSyncedAspect()
    // render
    return (
        <Container>
            {views.map(({ dataset, channel }, viewport) => {
                // get the sync state of the viewport
                const sync = synced[viewport]
                // render
                return (
                    <Viewport key={`${dataset.name}:${viewport}`}>
                        <Dataset>{dataset.name}</Dataset>
                        <Channel state={sync.channel} toggle={toggle(viewport, "channel")} />
                        <Zoom state={sync.zoom} toggle={toggle(viewport, "zoom")} />
                        <Scroll state={sync.scroll} toggle={toggle(viewport, "scroll")} />
                        <Path state={sync.path} toggle={toggle(viewport, "path")} />
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

// the viewport
const Index = styled(Cell)`
    text-align: right;
`

// the dataset
const Dataset = styled(Cell)`
    text-align: left;
    overflow: auto;
`


// end of file