// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
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
    // unpack the views
    const { views } = useFragment(bodyGetSyncTableFragment, qed)
    // render
    return (
        <Container>
            {views.map((view, viewport) => {
                // render
                return (
                    <Viewport key={`sync:${viewport}`}>
                        <Dataset viewport={viewport} view={view} />
                        <Channel viewport={viewport} view={view} mark={mark} />
                        <Zoom viewport={viewport} view={view} mark={mark} />
                        <Scroll viewport={viewport} view={view} mark={mark} />
                        <Path viewport={viewport} view={view} mark={mark} />
                        <Offset viewport={viewport} view={view} mark={mark} />
                    </Viewport>
                )
            })}
        </Container>
    )
}


const foo = () => {
    return (
        <>
        </>
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


// fragments
const bodyGetViewSyncStateFragment = graphql`
    fragment bodyGetViewSyncStateFragment on View {
        dataset {
            name
        }
        sync {
            dirty
            channel
            zoom
            scroll
            path
            offsets { x y }
        }
    }
`


const bodyGetSyncTableFragment = graphql`
    fragment bodyGetSyncTableFragment on QED {
        views {
            # individual entries
            # for the dataset column
            ...datasetSyncTableFragment
            # for the channel column
            ...channelSyncTableFragment
            # for the zoom column
            ...zoomSyncTableFragment
            # for the scroll column
            ...scrollSyncTableFragment
            # for the path column
            ...pathSyncTableFragment
            # for the offset column
            ...offsetSyncTableFragment
    }
}
`


// end of file