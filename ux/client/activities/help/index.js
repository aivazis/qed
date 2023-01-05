// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// widgets
import { Activity } from '~/activities'
// my shape
import { Help as Icon } from '~/shapes'
// styles
import styles from './styles'


// show the embedded documentation
export const Help = ({ size, style }) => {
    // mix my paint
    const paint = styles.activity(style)
    // and render
    return (
        <Activity size={size} url="/help" style={paint} >
            <Icon />
        </Activity>
    )
}


// end of file
