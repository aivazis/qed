// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { useLocation } from 'react-router-dom'

// locals
// widgets
import { Activity } from '~/activities'
// my shape
import { Flow as Icon } from '~/shapes'
// styles
import styles from './styles'


// edit the visualization pipeline of the active view
export const Flow = ({ size, disabled = false, style }) => {
    // get the current location
    const location = useLocation().pathname
    // my url
    const url = "/flow"
    // check whether i'm the current activity
    const current = location === url
    // mix my paint
    const paint = styles.activity(style)
    // and render
    return (
        <Activity size={size} url={url} current={current} disabled={disabled} style={paint}
            label="flow" >
            <Icon />
        </Activity>
    )
}

// end of file
