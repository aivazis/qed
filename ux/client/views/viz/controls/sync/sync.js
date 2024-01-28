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
// components
import { Header } from './header'
import { Body } from './body'

// the sync control
export const Sync = () => {
    // render
    return (
        <Tray title="sync" initially={true} state="enabled" scale={0.5}>
            <Housing>
                <Header />
                <Body />
            </Housing>
        </Tray>
    )
}

// the container
const Housing = styled.table`
    margin: 1.0em auto ;
    padding: 1.0em 0.0em ;
    font-family: inconsolata;
    color: hsl(0deg, 0%, 50%);
    margin: 0.0rem 0.5rem 0.5rem 0.5rem;
`


// end of file