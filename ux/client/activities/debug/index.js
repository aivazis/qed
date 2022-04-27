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
import { Hammer as Icon } from '~/shapes'
// styles
import styles from './styles'


// sandbox for experimenting with new features
export const Debug = ({ size, style }) => {
    // mix my paint
    const paint = styles.activity(style)
    // and render
    return (
        <Activity size={size} url="/graphiql" style={paint} >
            <Icon />
        </Activity>
    )
}


// end of file
