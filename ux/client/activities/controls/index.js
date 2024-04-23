// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { useLocation } from 'react-router-dom'

// locals
// widgets
import { Activity } from '~/activities'
// my shape
import { Gear as Icon } from '~/shapes'
// styles
import styles from './styles'


// access to the configuration of the visualization pipeline
export const Controls = ({ size, style }) => {
    // get the current location
    const location = useLocation().pathname
    // my url
    const url = "/controls"
    // check whether i'm the current activity
    const current = location === url
    // mix my paint
    const paint = styles.activity(style)
    // paint me
    return (
        <Activity size={size} url={url} current={current} style={paint} >
            <Icon />
        </Activity>
    )
}


// end of file
