// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { useLocation } from 'react-router-dom'

// locals
// widgets
import { Activity } from '~/activities'
// my shape
import { Data as Icon } from '~/shapes'
// styles
import styles from './styles'


// display the dataset selectors
export const Data = ({ size, style }) => {
    // get the current location
    const location = useLocation().pathname
    // my url
    const url = "/"
    // check whether i'm the current activity
    const current = location === url
    // mix my paint
    const paint = styles.activity(style)
    // and render
    return (
        <Activity size={size} url={url} current={current} style={paint} >
            <Icon />
        </Activity>
    )
}


// end of file
