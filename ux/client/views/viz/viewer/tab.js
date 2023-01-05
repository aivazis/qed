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
import { useViews } from '../viz/useViews'
// components
import { Collapse } from './collapse'
import { Measure } from './measure'
import { Print } from './print'
import { Selector } from './selector'
import { Split } from './split'
import { Sync } from './sync'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Tab = ({ viewport, view, behaviors }) => {
    // get the active view
    const { activeViewport } = useViews()
    // deduce my state
    const state = (viewport === activeViewport) ? "selected" : "enabled"
    // mix my paint
    const paint = styles.tab(state)
    // render
    return (
        <div style={paint} {...behaviors} >
            {/* the button that removes this view from the panel */}
            <Collapse viewport={viewport} />
            {/* the panel title */}
            {view && <Selector viewport={viewport} view={view} />}
            {/* some blank space */}
            <Spacer />
            {/* the button that toggles the data layer */}
            {view && <Measure viewport={viewport} />}
            {/* the button that toggles the sync status of the data viewport */}
            {view && <Sync viewport={viewport} />}
            {/* the button that prints the viewport */}
            {view && <Print viewport={viewport} />}
            {/* the button that adds a new view to the {viz} panel */}
            <Split viewport={viewport} />
        </div>
    )
}


// end of file