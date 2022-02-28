// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Target as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useMeasureLayer } from './useMeasureLayer'
import { useToggleMeasureLayer } from './useToggleMeasureLayer'
// styles
import styles from './styles'


// split a {view} into two
export const Measure = ({ viewport }) => {
    // get the current measure layer state
    const selected = useMeasureLayer()
    // grab the measure layer toggle from context
    const toggle = useToggleMeasureLayer()
    // turn it into a handler
    const measure = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // toggle
        toggle()
        // all done
        return
    }
    // assemble my controllers
    const behaviors = {
        onClick: measure
    }
    // deduce my state
    const state = selected ? "selected" : "enabled"
    // mix my paint
    const paint = styles.measure
    // and render
    return (
        <Badge size={14} state={state} behaviors={behaviors} style={paint} >
            <Icon />
        </Badge>
    )
}


// end of file