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
import { Provider } from './context'
// styles
import styles from './styles'


// the area
const Panel = () => {

    // render
    return (
        <Flex.Box direction="row" style={styles.flex} >

            {/* the explorer of datasets */}
            <Flex.Panel min={200} max={400} style={styles.datasets} >
                <Outlet />
            </Flex.Panel >

            {/* a visualization area */}
            <Flex.Panel style={styles.flex} auto={true} >
            </Flex.Panel >

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
