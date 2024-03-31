// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
// shapes
import { Target as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useToggleMeasureLayer } from '../measure'
// styles
import styles from './styles'


// split a {view} into two
export const Measure = ({ viewport, view }) => {
    // get the dataset in this view
    const { dataset, measure } = useFragment(measureViewerGetMeasureLayerStateFragment, view)
    // unpack its measure layer state
    const selected = measure.active

    // grab the measure layer toggle from context
    const { toggle } = useToggleMeasureLayer()
    // turn it into a handler
    const toggleMeasure = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // toggle
        toggle(dataset.name)
        // all done
        return
    }

    // assemble my controllers
    const behaviors = {
        onClick: toggleMeasure
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

// my fragment
const measureViewerGetMeasureLayerStateFragment = graphql`
    fragment measureViewerGetMeasureLayerStateFragment on View {
        dataset {
            name
        }
        measure {
            active
        }
    }
`


// end of file