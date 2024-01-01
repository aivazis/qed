// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// locals
// the activities
import { About, Controls, Data, Explore, Help, Kill } from '~/activities'
// widgets
import { Toolbar, Spacer } from '~/widgets'
// styles
import styles from './styles'


// the activity bar
export const Bar = ({ style }) => {
    // pick an icon size based in the screen resolution
    const rem = window.screen.width > 2048 ? 1.2 : 1.0
    // convert to pixels
    const size = rem * parseFloat(getComputedStyle(document.documentElement).fontSize)

    // mix my paint
    const paint = styles.bar(style)
    // paint me
    return (
        <Toolbar direction="column" style={paint} >
            <Explore size={size} style={paint} />
            <Data size={size} style={paint} />
            <Controls size={size} style={paint} />
            <Help size={size} style={paint} />

            <Spacer />

            <Kill size={size} style={paint} />
            <About size={size} style={paint} />
        </Toolbar>
    )
}


// end of file
