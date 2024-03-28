// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Spacer, Tray } from '~/widgets'
// colors
import { theme } from '~/palette'

// locals
// components
import { Body } from './body'
import { Header } from './header'
import { Reset } from './reset'
import { Save } from './save'

// the sync control
export const Sync = ({ qed }) => {
    // my state
    const [modified, setModified] = React.useState(false)

    // setup the reset action
    const reset = () => {
        // clear the flag
        setModified(false)
        // all done
        return
    }

    const mark = () => {
        // clear the flag
        setModified(true)
        // all done
        return
    }

    // render
    return (
        <Tray title="sync" initially={true} state="enabled" scale={0.5}>
            <Controls>
                <Spacer />
                <Save save={reset} enabled={modified} />
                <Reset reset={reset} enabled={modified} />
            </Controls>
            <Housing>
                <Header mark={mark} />
                <Body qed={qed} mark={mark} />
            </Housing>
        </Tray>
    )
}

const Controls = styled.div`
    height: 1.5rem;
    margin: 0.5rem 0.0rem 0.25rem 1.0rem;
    // for my children
    display: flex;
    flex-direction: row;
    align-items: center;
`

// the container
const Housing = styled.table`
    margin: 1.0em auto ;
    padding: 1.0em 0.0em ;
    color: ${() => theme.page.normal};
    margin: 0.0rem 0.5rem 0.5rem 0.5rem;
`


// end of file