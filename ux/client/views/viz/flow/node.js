// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useSelection } from './useSelection'


// position a node on  the diagram and add its behavior
export const Node = ({ id, position, children }) => {
    // unpack the position of the node
    const { x, y } = position
    // build the positioning transform
    const xform = `translate(${x} ${y})`

    // access the selection
    const { select } = useSelection()
    // a click picks me; with <shift>, it adds me to the selection or drops me from it
    const onClick = evt => {
        // the canvas clears the selection on a click, so keep this one to myself
        evt.stopPropagation()
        // pick me
        select(id, evt.shiftKey)
        // all done
        return
    }
    // node controls
    const nodeControls = { onClick }

    // render
    return (
        <g transform={xform} {...nodeControls} >
            {children}
        </g>
    )
}


// end of file
