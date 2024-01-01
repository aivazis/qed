// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { Colophon, Server, Spacer } from '~/widgets'
// locals
import styles from './styles'


// the bar at the bottom of every page
export const Status = () => (
    // the container
    <footer style={styles.box}>

        {/* version info and status of the app server */}
        <Server style={styles.server} />

        {/* render a separator */}
        <Spacer style={styles.spacer} />

        {/* the box with the copyright note */}
        <Colophon author="Michael&nbsp;Aïvázis" link="https://github.com/aivazis"
            span="1998-2024"
            style={styles.colophon} />

    </footer>
)


// end of file
