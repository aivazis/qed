// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
// paint
import styles from './styles'


// render a label
export const Label = ({ label, style }) => {
    // unpack
    const { id, at, value, category } = useFragment(labelFlowDiagramFragment, label)
    // mix the paint
    const paint = { ...styles.labels[category], ...style?.labels[category] }
    // render
    return (
        <text x={at.x} y={at.y} style={paint}>
            {value.join(", ")}
        </text>
    )
}


// my fragment
const labelFlowDiagramFragment = graphql`
    fragment labelFlowDiagramFragment on FlowLabel {
        # the id
        id
        # location
        at {
            x
            y
        }
        # state
        value
        category
    }
`

// end of file
