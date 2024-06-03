// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// project
// shapes
import { Flow as Shape } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// locals
// hooks
import { useFlowToggleLayer } from '../flow'
// styles
import styles from './styles'


// turn on the flow layer
export const Flow = ({ viewport, view }) => {
    // get the reader and flow layer in this view
    const { reader, flow } = useFragment(flowViewerGetFlowLayerStateFragment, view)
    // unpack its flow layer state
    const selected = flow.active

    // grab the flow layer toggle from context
    const { toggle } = useFlowToggleLayer()
    // toggle the flow layer
    const toggleFlow = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // quash the default behavior
        evt.preventDefault()
        // toggle
        toggle(viewport, reader.name)
        // all done
        return
    }

    // my event handlers
    const behaviors = {
        // toggle the flow state on a single click
        onClick: toggleFlow,
    }

    // set my state
    const state = selected ? "selected" : "enabled"
    // mix my paint
    const paint = styles.flow
    // render
    return (
        <Badge size={16} state={state} behaviors={behaviors} style={paint} >
            <Shape />
        </Badge >
    )
}

// my fragment
const flowViewerGetFlowLayerStateFragment = graphql`
    fragment flowViewerGetFlowLayerStateFragment on View {
        reader {
            name
        }
        flow {
            active
        }
    }
`


// end of file
