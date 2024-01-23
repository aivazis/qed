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

// the sync control
export const Sync = () => {
    // get the active view and unpack it
    const { views } = useViews()

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
                        <Header>scroll</Header>
                        <Header>zoom</Header>
                        <Header>viz</Header>
                    </Title>
                </Head>
                <Body>
                    {views.map(({ dataset, channel }, viewport) =>
                        <Viewport key={`${dataset.name}:${viewport}`}>
                            <Index>{`${viewport}:`}</Index>
                            <Dataset>{dataset.name}</Dataset>
                            <Channel></Channel>
                            <Scroll>+5 -3</Scroll>
                        </Viewport>
                    )}
                </Body>
            </Housing>
        </Tray>
    )
}

// the container
const Housing = styled.table`
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
    padding: 0.125rem;
    text-align: left;
`

// the table body
const Body = styled.tbody`
`

// viewport info
const Viewport = styled.tr`
`

// cells
const Cell = styled.td`
    padding: 0.125rem;
    text-align: left;
`

// the viewport
const Index = styled(Cell)`
    text-align: right;
`

// the dataset
const Dataset = styled(Cell)`
    overflow: auto;
`

// the channel
const Channel = styled(Cell)`
    overflow: auto;
`

// the scroll offset
const Scroll = styled(Cell)`
`


// end of file