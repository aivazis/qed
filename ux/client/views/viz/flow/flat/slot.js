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


// a slot seen from above: a dot, painted by whether it carries a product, by how far down its
// product is pinned, and by whether an instance has made it; a slot whose instance holds nothing
// is struck through
export const FlatSlot = ({ id, at, bound, level, empty, stale, selected }) => {
    // a slot is drawn as a product when it stands for one, or when an instance stands behind it,
    // whether or not it holds one
    const product = bound || level === "instance" || empty
    // decide what kind of slot to render
    const Shape = product ? Bound : Unbound
    // nothing is an outline, an instance is painted by whether it is stale, the rest by their level
    const key = empty ? "empty" : level === "instance" ? (stale ? "stale" : "fresh") : level
    // and that is how to paint a product
    const paint = product ? styles.levels.product[key] : undefined
    // assemble the graphic and render it
    return (
        <Node
            id={id} kind="slot" position={at}
            handles={{
                "data-qed-bound": bound, "data-qed-level": level,
                "data-qed-empty": empty, "data-qed-stale": stale,
            }}
        >
            <Shape highlight={selected} empty={empty} style={paint} />
        </Node>
    )
}


// end of file
