// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// locals
// the activities
import { About, Data, Debug, Help, Kill } from '~/activities'
// widgets
import { Toolbar, Spacer } from '~/widgets'
// styles
import styles from './styles'


// the activity bar
const bar = () => {
    // decide on a size
    const size = 32

    // paint me
    return (
        <Toolbar direction="column" style={styles} >
            <Data size={size} style={styles} />
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
