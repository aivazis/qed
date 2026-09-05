// -*- web -*-
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
import { Console as Icon } from '~/shapes'
// styles
import styles from './styles'


// display the journal console
export const Console = ({ size, style }) => {
    // get the current location
    const location = useLocation().pathname
    // my url
    const url = "/console"
    // check whether i'm the current activity
    const current = location === url
    // mix my paint
    const paint = styles.activity(style)
    // and render
    return (
        <Activity size={size} url={url} current={current} style={paint} label="journal" >
            <Icon />
        </Activity>
    )
}


// end of file
