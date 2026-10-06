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
// the projection
import { useProjection } from './projection'
// paint
import styles from './styles'


// render a label
export const Label = ({ label, style }) => {
    // unpack
    const { id, at, value, category, owner } = useFragment(labelFlowDiagramFragment, label)
    // a label follows its node while it is dragged
    const { dx, dy, dz } = useDrag().shiftOf(owner)
    // the projection
    const { project, labelLift } = useProjection()
    // seen from the side, above a node means up, rather than further back on the floor, so a
    // label that floats above its node moves from behind it to over it
    const lift = labelLift(category)
    // where the label goes
    const { x, y } = project({ x: at.x + dx, y: at.y + dy + lift, z: (at.z ?? 0) + dz + lift })
    // mix the paint
    const paint = { ...styles.labels[category], ...style?.labels[category] }
    // render
    return (
        <text x={x} y={y} style={paint}
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
            z
        }
        # state
        value
        category
        # the node i follow while it is dragged
        owner
    }
`


// end of file
