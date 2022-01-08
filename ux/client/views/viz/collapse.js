// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { X } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useCollapseView } from './useCollapseView'
// styles
import styles from './styles'


// remove a {view} from the {viz} panel
export const Collapse = ({ view }) => {
    // make a handler that that collapses this view
    const collapse = { onClick: useCollapseView(view) }

    // grab my style
    const collapseStyle = styles.collapse

    // render
    return (
        <Badge size={10} state="available" behaviors={collapse} style={collapseStyle} >
            <X style={collapseStyle} />
        </Badge>
    )
}


// end of file