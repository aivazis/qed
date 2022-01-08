// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Split as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useSplitView } from './useSplitView'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Split = ({ view }) => {
    // make a handler that splits this view
    const split = { onClick: useSplitView(view) }

    // grab my style
    const splitStyle = styles.split

    // render
    return (
        <Badge size={10} state="available" behaviors={split} style={splitStyle} >
            <Icon style={splitStyle} />
        </Badge>
    )
}


// end of file