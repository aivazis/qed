// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Slot as Unbound, Product as Bound } from '~/shapes'

// local
// components
import { Node } from '../node'
// styles
import styles from '../styles'


// a slot seen from above: a dot, painted by whether it carries a product, and by how far down
// its product is pinned
export const FlatSlot = ({ id, at, bound, level, selected }) => {
    // decide what kind of slot to render
    const Shape = bound ? Bound : Unbound
    // and how to paint a product
    const paint = bound ? styles.levels.product[level] : undefined
    // assemble the graphic and render it
    return (
        <Node
            id={id} kind="slot" position={at}
            handles={{ "data-qed-bound": bound, "data-qed-level": level }}
        >
            <Shape highlight={selected} style={paint} />
        </Node>
    )
}


// end of file
