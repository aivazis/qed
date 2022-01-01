// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
// framework
import React from 'react'
// routing
import { Outlet } from 'react-router-dom'

// locals
// context
import { Provider } from './context'
// view
import { Status } from '~/views'
// activities
import { ActivityBar } from '~/activities'
// styles
import styles from './styles'


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


// turn the panel into a context provider
export const Main = () => {
    // set up the context provider
    return (
        <Provider >
            <Panel />
        </Provider>
    )
}


// end of file
