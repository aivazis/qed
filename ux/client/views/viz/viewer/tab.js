// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'


// project
// widgets
import { Spacer } from '~/widgets'

// locals
// components
import { Collapse } from './collapse'
import { Selector } from './selector'
import { Split } from './split'
import { Sync } from './sync'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Tab = ({ viewport, view, behaviors }) => {
    // mix my paint
    const paint = styles.tab
    // render
    return (
        <div style={paint} {...behaviors} >
            {/* the button that removes this view from the panel */}
            <Collapse viewport={viewport} />

            {view && (
                <>
                    <Selector viewport={viewport} view={view} />
                    {/* some blank space */}
                    <Spacer />
                    {/* the button that adds a new view to the {viz} panel */}
                    <Split viewport={viewport} />
                    {/* the button that toggles the sync status of the data viewport */}
                    <Sync viewport={viewport} />
                </>
            )}
        </div>
    )
}


// end of file