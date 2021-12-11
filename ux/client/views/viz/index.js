// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
// routing
import { Outlet } from 'react-router-dom'

// project
// widgets
import { Flex } from '~/widgets'

// locals
// context
import { Context, Provider } from './context'
// the blank view
import { Blank } from './blank'
// styles
import styles from './styles'


// the area
const Panel = () => {
    // grab the views
    const { views } = React.useContext(Context)

    // render
    return (
        <Flex.Box direction="row" style={styles.flex} >

            {/* the explorer of datasets */}
            <Flex.Panel min={200} max={400} style={styles.datasets} >
                <Outlet />
            </Flex.Panel >

            {views.length == 0 &&
                <Flex.Panel style={styles.flex} auto={true} >
                    <Blank />
                </Flex.Panel >
            }
            {views.map(idx =>
                <Flex.Panel style={styles.flex} auto={true} >
                </Flex.Panel >
            )}

        </Flex.Box >
    )
}


// turn the view into a context provider and publish
export const Viz = ({ }) => {
    // set up the context provider
    return (
        <Provider >
            <Panel />
        </Provider>
    )
}


// export the panels
export { Controls } from './controls'
export { Datasets } from './datasets'


// end of file
