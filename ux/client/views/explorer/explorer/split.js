// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


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
import { split as splitPaint } from './styles'


// split a {view} into two
export const Split = ({ viewport }) => {
    // grab the hook that splits a {view}
    const splitView = useSplitView(viewport)
    // turn it into a handler that splits this {view}
    const split = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // manage the {view} state
        splitView()
        // all done
        return
    }

    // assemble the controllers to hand my {badge}
    const behaviors = {
        onClick: split,
    }

    // mix my paint
    const paint = splitPaint
    // and render
    return (
        <Badge size={16} state="enabled" behaviors={behaviors} style={paint} >
            <Icon />
        </Badge>
    )
}


// end of file