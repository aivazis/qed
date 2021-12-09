// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
// framework
import React from 'react'
// routing
import { Outlet } from 'react-router-dom'

// locals
import styles from './styles'
// view
import { Status } from '~/views'
// activities
import { ActivityBar } from '~/activities'


// the main app working area
// the layout is simple: the activity bar and activity dependent routing
const Panel = () => {
    // lay out the main page
    return (
        <section style={styles.page} >
            <section style={styles.panel} >
                {/* navigation bar */}
                <ActivityBar style={styles.activitybar} />
                {/* the client area */}
                <Outlet />

            </section >
            <Status />
        </section >
    )
}


// publish
export default Panel


// end of file
