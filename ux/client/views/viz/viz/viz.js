// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
// routing
import { Outlet } from 'react-router-dom'

// project
// hooks
import { useActivityPanel } from '~/views'
// widgets
import { Flex } from '~/widgets'

// local
// context
import { VizProvider } from './context'
// hooks
import { useViewports } from './useViewports'
import { useInitializeViewports } from './useInitializeViewports'
import { useMakePanDispatcher } from './useMakePanDispatcher'
// components
import { Viewer } from '../viewer'
// paint
import styles from './styles'


// turn my panel into a context provider and publish it
export const Viz = ({ qed }) => (
    <VizProvider>
        <VizPanel qed={qed} />
    </VizProvider>
)

// the flex panel factory
const VizPanel = ({ qed }) => {
    // ask the server side store for all known data readers and attach them as read-only state
    const { views } = useFragment(vizGetViewsFragment, qed)
    // initialize my pile of viewports and get the ref registrar
    // viewport initialization happens on every render, but so does viewport registration
    const { viewportRegistrar } = useInitializeViewports(views)
    // build the scroll handler dispatch for my viewports
    const { dispatch } = useMakePanDispatcher()
    // get the view activator
    const { activate } = useViewports()
    // get the state of the activity panel
    const { activityPanel } = useActivityPanel()

    // mix my paint
    // make a copy of the activity panel paint
    const activityPaint = { ...styles.activityPanels }
    // so we can hide it when its not visible
    activityPaint.panel.display = activityPanel ? "flex" : "none"

    // render
    return (
        <Flex.Box direction="row" style={styles.flex}>
            {/* the panel with activity specific content, as determined by the current route */}
            <Flex.Panel min={350} style={activityPaint} >
                <Outlet />
            </Flex.Panel>

            {/* a panel for each registered view */}
            {views.map((view, viewport) => {
                // make a registrar for this {viewport}
                const registrar = viewportRegistrar(viewport)
                // assemble the behaviors by invoking the handler factories
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
                    </Flex.Panel>
                )
            })}

        </Flex.Box>
    )
}


// my fragment
const vizGetViewsFragment = graphql`
    fragment vizGetViewsFragment on QED {
        views {
            id
            # plus what viewers and their parts need
            ...viewerGetViewFragment
            ...infoViewerGetViewFragment
            ...selectorViewerGetViewFragment
            ...viewportViewerGetViewFragment

        }
    }
`


// end of file
