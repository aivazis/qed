// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// widgets
import { Activity } from '~/activities'
// my shape
import { Gear as Icon } from '~/shapes'
// styles
import styles from './styles'


// access to the configuration of the visualization pipeline
export const Controls = ({ size, style }) => {
    // mix my paint
    const paint = styles.activity(style)
    // paint me
    return (
        <Activity size={size} url="/controls" style={paint} >
            <Icon />
        </Activity>
    )
}


// end of file
