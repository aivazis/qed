// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'


// project
// widgets
import { Spacer } from '~/widgets'

// locals
// hooks
import { useViews } from './useViews'
// components
import { Collapse } from './collapse'
import { Selector } from './selector'
import { Split } from './split'
// styles
import { tab as paintTab } from './styles'


// display the datasets associated with this reader
export const Tab = ({ viewport, view, behaviors }) => {
    // get the active viewport
    const { activeViewport } = useViews()
    // deduce my state
    const state = (viewport === activeViewport) ? "selected" : "enabled"
    // mix my paint
    const paint = paintTab(state)
    // render
    return (
        <div style={paint} {...behaviors} >
            {/* the button that removes this view from the panel */}
            <Collapse viewport={viewport} />
            {/* the panel title */}
            {view?.archive && <Selector viewport={viewport} view={view} />}
            {/* some blank space */}
            <Spacer />
            {/* the button that adds a new view to the {roster} panel */}
            <Split viewport={viewport} />
        </div>
    )
}


// end of file