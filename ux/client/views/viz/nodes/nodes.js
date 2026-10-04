// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Header } from '~/widgets'

// locals
// styles
import styles from './styles'


// the panel with the nodes that a visualization pipeline can be built out of; while it is up,
// the active view shows its pipeline below its data
export const Nodes = () => {
    // render
    return (
        <Panel data-qed-panel="flow">
            {/* the title of the panel */}
            <Header title="flow nodes" style={styles.header} />
        </Panel>
    )
}


// the container
const Panel = styled.div`
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
`

// end of file
