// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// locals
// widgets
import { Activity } from '~/activities'
// my shape
import { Pin as Icon } from '~/shapes'
// styles
import styles from './styles'


// display the dataset selectors
export const Explore = ({ size, style }) => {
    // mix my paint
    const paint = styles.activity(style)
    // and render
    return (
        <Activity size={size} url="/explore" style={paint} >
            <Icon />
        </Activity>
    )
}


// end of file
