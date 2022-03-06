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
import { Demo } from '../demo'
import { Zoom } from './zoom'
// styles
import styles from './styles'


// export the activity panel
export const Controls = () => {
    // render
    return (
        <>
            {/* the title of the panel */}
            <Header title="controls" style={styles.header} />
            {/* the controls common to all datasets */}
            <Zoom />
            {/* my play area */}
            <Demo />
        </>
    )
}


// end of file
