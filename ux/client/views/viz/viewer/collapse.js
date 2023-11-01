// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { X as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useCollapseView } from '../viz/useCollapseView'
// styles
import styles from './styles'


// remove a {viewport} from the {viz} panel
export const Collapse = ({ viewport }) => {
    // grab the hook that collapses a {viewport}
    const collapseView = useCollapseView()
    // turn it into a handler that collapses this {viewport}
    const collapse = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // manage the {viewport} state
        collapseView(viewport)
        // all done
        return
    }

    // assemble the controllers to hand to my {badge}
    const behaviors = {
        onClick: collapse,
    }

    // mix my paint
    const paint = styles.collapse
    // and render
    return (
        <Badge size={10} state="enabled" behaviors={behaviors} style={paint} >
            <Icon />
        </Badge>
    )
}


// end of file