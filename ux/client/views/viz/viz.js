// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


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
// hooks
import { useViews } from './useViews'
import { useViewports } from './useViewports'
import { useSetActiveView } from './useSetActiveView'
import { useMakePanDispatcher } from './useMakePanDispatcher'
// components
import { Blank } from './blank'
import { Viewer } from './viewer'
// styles
import styles from './styles'


// the area
const Panel = () => {
    // grab the registered views
    const { views } = useViews()
    // get the view activator
    const activate = useSetActiveView()
    // the state of the activity panel
    const { activityPanel } = useActivityPanel()
    // get my pile of viewports and the ref registrar
    const { viewports, registrar } = useViewports()
    // build the scroll handler dispatch for my viewports
    const dispatch = useMakePanDispatcher(viewports)

    // paint mixing
    const datasetPaint = { ...styles.datasets }
    // if the activity panel is not visible hide it
    datasetPaint.panel.display = activityPanel ? "flex" : "none"

    // render
    return (
        <Flex.Box direction="row" style={styles.flex} >
            {/* panel with activity specific content, determined by the current route */}
            <Flex.Panel min={250} max={450} style={datasetPaint} >
                <Outlet />
            </Flex.Panel >

            { /* a blank panel when there are no datasets to render */}
            {views.length == 0 &&
                <Flex.Panel style={styles.flex} auto={true} >
                    <Blank />
                </Flex.Panel >
            }

            {/* otherwise, make a flex panel with a viewer for each registered view */}
            {views.map((view, idx) => {
                // the handler for activating the view is attached to the flex panel because
                // the {viewer} is just a react fragment
                return (
                    <Flex.Panel key={`panel:${idx}`}
                        auto={true}
                        style={styles.flex}
                        onClick={activate(idx)}
                        onScrollCapture={dispatch(idx)}
                    >
                        <Viewer idx={idx} view={view} registrar={registrar(idx)} />
                    </Flex.Panel >
                )
            })}

        </Flex.Box >
    )
}


// context
import { VizProvider } from './vizContext'
// turn the view into a context provider and publish
export const Viz = ({ }) => {
    // set up the context provider
    return (
        <VizProvider >
            <Panel />
        </VizProvider>
    )
}


// end of file
