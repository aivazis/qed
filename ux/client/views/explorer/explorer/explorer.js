// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

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
// paint
import { activityPanels as panelPaint, flex as flexPaint } from './styles'

// export the context provider
export const Explorer = () => {
    // set up the context provider
    return (
        <Provider>
            <Panel />
        </Provider>
    )
}


// my panel
const Panel = () => {
    // mix my paint
    // the state of the activity panel
    const { activityPanel } = useActivityPanel()
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
        </Flex.Box>
    )
}


// end of file
