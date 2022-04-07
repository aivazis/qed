// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

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
            <Viz />
        </>
    )
}


// end of file
