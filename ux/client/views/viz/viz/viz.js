// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


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
    // extract an array with the scroll sync flag for each viewport
    const synced = views.map(view => view.sync)
    // initialize my pile of viewports and get the ref registrar
    // viewport initialization happens on every render, but so does viewport registration
    const { viewportRegistrar } = useInitializeViewports(views)
    // get the viewport information
    const { activate, viewports } = useViewports()
    // build the scroll handler dispatch for my viewports
    const { dispatch } = useMakePanDispatcher({ viewports, synced })
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


// my fragments
const vizGetViewsFragment = graphql`
    fragment vizGetViewsFragment on QED {
        views {
            # MGA:
            # this is a copy-paste of my vizGetScrollSyncedViewsFragment
            # is there a way to avoid this duplication?
            id
            sync {
                scroll
                offsets {
                    x
                    y
                }
            }
            # what i need for synced scrolling
            ...vizGetScrollSyncedViewsFragment
            # for the measure layer
            ...measureGetMeasureLayerFragment
            # what viewers and their parts need
            ...viewerGetViewFragment
            ...selectorViewerGetViewFragment
            ...viewportViewerGetViewFragment
            # for the info widget with the dataset metadata
            ...infoViewerGetViewFragment
            # for the measure control
            ...measureViewerGetMeasureLayerStateFragment
            # for the sync control
            ...syncViewerGetScrollSyncStateFragment
            # for the print button
            ...printViewerGetViewFragment
            # for the measure control
            ...measureControlsGetMeasureLayerStateFragment
            ...minimapControlsGetMeasureLayerStateFragment
            ...profileMeasureGetMeasureLayerFragment
            # for the zoom control
            ...zoomControlsGetZoomStateFragment
            # for the viz control
            ...vizControlsGetViewFragment
            # for the sync table
            ...bodyGetViewSyncStateFragment
        }
    }
`

const vizGetScrollSyncedViewsFragment = graphql`
   fragment vizGetScrollSyncedViewsFragment on View {
        id
        sync {
            scroll
            offsets {
                x
                y
            }
        }
   }
`


// end of file
