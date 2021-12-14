// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// locals
// the activities
import { About, Controls, Data, Debug, Help, Kill } from '~/activities'
// widgets
import { Toolbar, Spacer } from '~/widgets'
// styles
import styles from './styles'


// the activity bar
const bar = () => {
    // pick an icon size based in the screen resolution
    const rem = window.screen.width > 2048 ? 1.2 : 1.0
    // convert to pixels
    const size = rem * parseFloat(getComputedStyle(document.documentElement).fontSize)

    // paint me
    return (
        <Toolbar direction="column" style={styles} >
            <Data size={size} style={styles} />
            <Controls size={size} style={styles} />
            <Help size={size} style={styles} />
            <Debug size={size} style={styles} />

            <Spacer />

            <Kill size={size} style={styles} />
            <About size={size} style={styles} />
        </Toolbar>
    )
}


// publish
export default bar


// end of file
