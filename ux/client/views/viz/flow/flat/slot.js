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


// a slot seen from above: a dot, painted by whether it carries a product
export const FlatSlot = ({ id, at, bound, selected }) => {
    // decide what kind of slot to render
    const Shape = bound ? Bound : Unbound
    // assemble the graphic and render it
    return (
        <Node id={id} kind="slot" position={at} handles={{ "data-qed-bound": bound }}>
            <Shape highlight={selected} />
        </Node>
    )
}


// end of file
