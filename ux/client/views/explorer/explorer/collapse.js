// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { X as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useCollapseViewport } from './useCollapseViewport'
// styles
import { collapse as collapsePaint } from './styles'


// remove a {viewport} from the {roster} panel
export const Collapse = ({ viewport }) => {
    // grab the hook that collapses a {viewport}
    const collapseViewport = useCollapseViewport(viewport)
    // turn it into a handler that collapses this {viewport}
    const collapse = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // manage the {viewport} state
        collapseViewport()
        // all done
        return
    }

    // assemble the controllers to hand to my {badge}
    const behaviors = {
        onClick: collapse,
    }

    // and render
    return (
        <Badge size={10} state="enabled" behaviors={behaviors} style={collapsePaint} >
            <Icon />
        </Badge>
    )
}


// end of file