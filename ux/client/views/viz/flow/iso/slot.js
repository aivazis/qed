// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// components
import { Node } from '../node'
import { Puck } from './solids'
// paint
import styles from '../styles'


// a slot seen from the side: a puck, painted by whether it carries a product, by how far down its
// product is pinned, and by whether an instance has made it; a slot whose instance holds nothing
// is struck through
export const IsoSlot = ({ id, at, bound, level, empty, stale, selected }) => {
    // a slot is drawn as a product when it stands for one, or when an instance stands behind it,
    // whether or not it holds one
    const product = bound || level === "instance" || empty
    // nothing is an outline, an instance is painted by whether it is stale, the rest by their level
    const key = empty ? "empty" : level === "instance" ? (stale ? "stale" : "fresh") : level
    // render
    return (
        <Node
            id={id} kind="slot" position={at}
            handles={{
                "data-qed-bound": bound, "data-qed-level": level,
                "data-qed-empty": empty, "data-qed-stale": stale,
            }}
        >
            <Puck
                highlight={selected}
                empty={empty}
                paint={product ? styles.isoLevels.product[key] ?? styles.iso.product : styles.iso.slot}
            />
        </Node>
    )
}


// end of file
