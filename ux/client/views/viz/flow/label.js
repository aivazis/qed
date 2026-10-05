// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// local
// the drag in progress
import { useDrag } from './drag'
// paint
import styles from './styles'


// render a label
export const Label = ({ label, style }) => {
    // unpack
    const { id, at, value, category, owner } = useFragment(labelFlowDiagramFragment, label)
    // a label follows its node while it is dragged
    const { dx, dy } = useDrag().shiftOf(owner)
    // mix the paint
    const paint = { ...styles.labels[category], ...style?.labels[category] }
    // render
    return (
        <text x={at.x + dx} y={at.y + dy} style={paint}
            data-qed-label={category} data-qed-owner={owner ?? undefined}>
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
        # the node i follow while it is dragged
        owner
    }
`


// end of file
