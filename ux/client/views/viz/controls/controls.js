// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Header } from '~/widgets'

// locals
// hooks
import { useGetView } from '../viz/useGetView'
// components
import { Measure } from './measure'
import { Zoom } from './zoom'
import { Viz } from './viz'
// styles
import styles from './styles'


// export the activity panel
export const Controls = () => {
    // unpack the active view
    const { dataset, channel } = useGetView()
    // disable some trays if either dataset or channel are trivial
    const enabled = (dataset != null) && (channel != null)

    // render
    return (
        <React.Suspense fallback={<Loading />}>
            {/* the title of the panel */}
            <Header title="controls" style={styles.header} />
            {/* controls for the measuring layer */}
            {enabled && <Measure />}
            {/* the controls common to all datasets */}
            {enabled && <Zoom />}
            {/* visualization pipeline controls */}
            {enabled && <Viz />}
        </React.Suspense>
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
