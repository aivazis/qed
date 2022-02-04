// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Tray } from '~/widgets'

// locals
// styles
import styles from './styles'


// display the zoom control
export const Zoom = () => {

    // set up my state
    const state = "enabled"

    // mix my paint
    const paint = styles.zoom(state)
    // and render
    return (
        <Tray title="zoom" initially={true} style={paint.tray}>
        </Tray>
    )
}


// end of file
