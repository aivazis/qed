// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { X } from '~/shapes'

// local
// hooks
import { useAnchorRemove } from '~/views/viz/measure'
// components
import { Button } from './button'


// remove this point from the path
export const Delete = ({ viewport, idx }) => {
    // get the path mutator that can delete a point
    const { remove } = useAnchorRemove(viewport)

    // build the handler
    const handler = () => {
        // remove the node from the path
        remove({ anchor: idx })
        // all done
        return
    }
    // assemble the behaviors
    const behaviors = {
        onClick: handler,
    }

    // render
    return (
        <Button size={12} behaviors={behaviors}>
            <X />
        </Button>
    )
}


// end of file
