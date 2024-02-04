// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { X } from '~/shapes'

// local
// hooks
import { useSetPixelPath } from '../../../viz/useSetPixelPath'
// components
import { Button } from './button'


// remove this point from the path
export const Delete = ({ idx }) => {
    // get the path mutator that can delete a point
    const { remove } = useSetPixelPath()

    // build the handler
    const handler = () => {
        // remove the node from the path
        remove(idx)
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
