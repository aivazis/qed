// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from '~/palette'

// local
// hooks
import { useViewports } from '~/views/viz'
import { useSyncToggleAll } from './useSyncToggleAll'


// the sync control table header
export const Header = ({ mark }) => {
    // get the set of views
    const { activeViewport } = useViewports()
    // get the sync handler factories
    const { toggle } = useSyncToggleAll()
    // a behavior factory
    const behaviors = aspect => {
        // build the table of behaviors and return it
        return {
            onClick: evt => {
                // stop this event from bubbling up
                evt.stopPropagation()
                // and quash any side effects
                evt.preventDefault()
                // update the entire column based on the state of the active viewport
                toggle({ viewport: activeViewport, aspect })
                // mark the control as modified
                mark()
                // all done
                return
            }
        }
    }
    // render
    return (
        <Head>
            <Title>
                <Column></Column>
                <ActiveColumn {...behaviors("channel")}>channel</ActiveColumn>
                <ActiveColumn {...behaviors("zoom")}>zoom</ActiveColumn>
                <ActiveColumn {...behaviors("scroll")}>scroll</ActiveColumn>
                <ActiveColumn {...behaviors("path")}>path</ActiveColumn>
                <Column>offsets</Column>
            </Title>
        </Head>
    )
}


// headers
const Head = styled.thead`
`

const Title = styled.tr`
`

const Column = styled.th`
    font-family: rubik-light;
    font-weight: normal;
    text-align: center;
    vertical-align: middle;
    padding: 0.5em 0.0em ;
    cursor: default;
`

const ActiveColumn = styled(Column)`
    & {
        cursor: pointer;
    }

    &:hover {
        color: ${() => theme.page.highlight};
    }
`


// end of file