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

// local
// context
import { Provider } from './context'
// hooks
import { useViews } from './useViews'
import { useSetActiveViewport } from './useSetActiveViewport'
import { useInitializeViewports } from './useInitializeViewports'
import { useMakePanDispatcher } from './useMakePanDispatcher'
// components
import { Viewer } from '../viewer'
// paint
import styles from './styles'


// export the view
export const Viz = () => {
    // set up the context provider and embed my panel
    return (
        <Provider>
            <Panel />
        </Provider>
    )
}


// my panel
const Panel = () => {
    // the state of the activity panel
    const { activityPanel } = useActivityPanel()
    // the set of known views
    const { views } = useViews()
    // initialize my pile of viewports and get the ref registrar
    // viewport initialization happens on every render, but so does viewport registration
    const { viewportRegistrar } = useInitializeViewports()
    // build the scroll handler dispatch for my viewports
    const dispatch = useMakePanDispatcher()
    // get the view activator
    const activate = useSetActiveViewport()

    // mix my paint
    // make a copy of the activity panel paint
    const activityPaint = { ...styles.activityPanels }
    // so we can hide it when its not visible
    activityPaint.panel.display = activityPanel ? "flex" : "none"

    // render
    return (
        <Flex.Box direction="row" style={styles.flex}>
            {/* the panel with activity specific content, as determined by the current route */}
            <Flex.Panel min={250} max={450} style={activityPaint} >
                <Outlet />
            </Flex.Panel >

            {/* a panel for each registered view */}
            {views.map((view, viewport) => {
                // make a registrar for this {viewport}
                const registrar = viewportRegistrar(viewport)
                // assemble the behaviors
                const behaviors = {
                    onClick: activate(viewport),
                    onScrollCapture: dispatch(viewport),
                }
                // the view behaviors are attached to the flex panel because the {viewer} is not
                // a real container, just a react fragment
                return (
                    <Flex.Panel key={`panel:${viewport}`}
                        auto={true}
                        style={styles.flex} {...behaviors}
                    >
                        <Viewer viewport={viewport} view={view} registrar={registrar} />
                    </Flex.Panel >
                )
            })}

        </Flex.Box>
    )
}

// end of file
