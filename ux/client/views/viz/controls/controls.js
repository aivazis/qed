// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Header } from '~/widgets'

// locals
// components
import { Measure } from './measure'
import { Zoom } from './zoom'
import { Viz } from './viz'
// styles
import styles from './styles'


// export the activity panel
export const Controls = () => {
    // render
    return (
        <>
            {/* the title of the panel */}
            <Header title="controls" style={styles.header} />
            {/* controls for the measuring layer */}
            <Measure />
            {/* the controls common to all datasets */}
            <Zoom />
            {/* visualization pipeline controls */}
            <React.Suspense fallback={<Loading />}>
                <Viz />
            </React.Suspense>
        </>
    )
}


const Loading = styled.div`
    font-family: inconsolata;
    font-size: 75%;
    cursor: default;
    padding: 0.25rem;
    content: "loading";
`

// end of file
