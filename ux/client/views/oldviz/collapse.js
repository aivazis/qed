// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { X as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useCollapseView } from './useCollapseView'
// styles
import styles from './styles'


// remove a {view} from the {viz} panel
export const Collapse = ({ view }) => {
    // grab the hook that collapses a {view}
    const collapseView = useCollapseView(view)
    // turn it into a handler that collapses this {view}
    const collapse = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // manage the {view} state
        collapseView()
        // all done
        return
    }

    // assemble the controllers to hand my {badge}
    const behaviors = {
        onClick: collapse,
    }

    // mix my paint
    const collapseStyle = styles.collapse

    // render
    return (
        <Badge size={10} state="available" behaviors={behaviors} style={collapseStyle} >
            <Icon style={collapseStyle} />
        </Badge>
    )
}


// end of file