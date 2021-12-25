// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
// routing
import { Outlet } from 'react-router-dom'

// project
// hooks
import { useActivityPanel } from '~/views'
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
    // get the state of the activity panel
    const { activityPanel } = useActivityPanel()
    // grab the views
    const { views } = React.useContext(Context)

    // paint mixing
    const datasetPaint = { ...styles.datasets }
    // if the activity panel is not visible hide it
    datasetPaint.panel.display = activityPanel ? "flex" : "none"

    // render
    return (
        <Flex.Box direction="row" style={styles.flex} >
            {/* panel with activity specific content, determined by the current route */}
            <Flex.Panel min={200} max={400} style={datasetPaint} >
                <Outlet />
            </Flex.Panel >

            { /* a blank panel when there are no datasets to render */}
            {views.length == 0 &&
                <Flex.Panel style={styles.flex} auto={true} >
                    <Blank />
                </Flex.Panel >
            }

            {/* otherwise, make a panel for each active view */}
            {views.map(({ dataset, channel }, idx) =>
                <Flex.Panel key={`${dataset}:${channel}`} style={styles.flex} auto={true} >
                    <Blank idx={idx} />
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


// end of file
