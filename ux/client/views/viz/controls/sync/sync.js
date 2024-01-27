// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Tray } from '~/widgets'

// locals
// hooks
import { useViews } from '../../viz/useViews'
import { useSynced } from '../../viz/useSynced'
// components
import { Cell } from './cell'
import { Channel } from './channel'
import { Zoom } from './zoom'

// the sync control
export const Sync = () => {
    // get the set of views
    const { views } = useViews()
    // get the sync state of all the viewports
    const synced = useSynced()

    console.log(views)

    // render
    return (
        <Tray title="sync" initially={true} state="enabled" scale={0.5}>
            <Housing>
                <Head>
                    <Title>
                        <Header></Header>
                        <Header></Header>
                        <Header>channel</Header>
                        <Header>zoom</Header>
                        <Header>scroll</Header>
                        <Header>path</Header>
                    </Title>
                </Head>
                <Body>
                    {views.map(({ dataset, channel }, viewport) => {
                        // get the sync state of the viewport
                        const sync = synced[viewport]
                        // unpack the scroll offset
                        const offset = sync.scroll ? [
                            sync.scroll.x.toString(),
                            sync.scroll.y.toString(),
                        ].join(" ") : "no"
                        // render
                        return (
                            <Viewport key={`${dataset.name}:${viewport}`}>
                                <Index>{`${viewport}:`}</Index>
                                <Dataset>{dataset.name}</Dataset>
                                <Channel />
                                <Zoom />
                                <Scroll>{offset}</Scroll>
                            </Viewport>
                        )
                    })}
                </Body>
            </Housing>
        </Tray>
    )
}

// the container
const Housing = styled.table`
    margin: 1.0em auto ;
    padding: 1.0em;
    font-family: inconsolata;
    color: hsl(0deg, 0%, 50%);
    margin: 0.0rem 0.5rem 0.5rem 0.5rem;
`

// headers
const Head = styled.thead`
`

const Title = styled.tr`
`

const Header = styled.th`
    font-family: rubik-light;
    font-weight: normal;
    text-align: center;
    vertical-align: middle;
`

// the table body
const Body = styled.tbody`
    font-size: 100%;
`

// viewport info
const Viewport = styled.tr`
`

// the viewport
const Index = styled(Cell)`
    text-align: right;
`

// the dataset
const Dataset = styled(Cell)`
    overflow: auto;
`


// the scroll offset
const Scroll = styled(Cell)`
`


// end of file