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


// a slot seen from the side: a puck, painted by whether it carries a product
export const IsoSlot = ({ id, at, bound, selected }) => {
    // render
    return (
        <Node id={id} kind="slot" position={at} handles={{ "data-qed-bound": bound }}>
            <Puck highlight={selected} paint={bound ? styles.iso.product : styles.iso.slot} />
        </Node>
    )
}


// end of file
