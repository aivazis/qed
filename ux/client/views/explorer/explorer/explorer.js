// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved

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
// components
import { Viewer } from './viewer'
// paint
import { activityPanels as panelPaint, flex as flexPaint } from './styles'

// export the context provider
export const Explorer = ({ qed }) => {
    // set up the context provider
    return (
        <Provider qed={qed}>
            <Panel />
        </Provider>
    )
}


// my panel
const Panel = () => {
    // the state of the activity panel
    const { activityPanel } = useActivityPanel()

    // the registered views
    const { views } = useViews()
    // get the view activator
    const activateViewport = useSetActiveViewport()

    // mix my paint
    // make a copy of the activity panel paint
    const activityPaint = { ...panelPaint }
    // so we can hide it when its not visible
    activityPaint.panel.display = activityPanel ? "flex" : "none"
    // render
    return (
        <Flex.Box direction="row" style={flexPaint}>
            {/* the panel with activity specific content, as determined by the current route */}
            <Flex.Panel min={200} style={activityPaint} >
                <Outlet />
            </Flex.Panel>

            {/* a panel for each registered view */}
            {views.map((view, viewport) => {
                // assemble the behaviors
                const behaviors = {
                    onClick: activateViewport(viewport),
                }
                // the view behaviors are attached to the flex panel because the {viewer} is not
                // a real container, just a react fragment
                return (
                    <Flex.Panel key={`panel:${viewport}`}
                        auto={true}
                        style={flexPaint} {...behaviors}
                    >
                        <Viewer viewport={viewport} view={view} />
                    </Flex.Panel>
                )
            })}

        </Flex.Box>
    )
}


// end of file
