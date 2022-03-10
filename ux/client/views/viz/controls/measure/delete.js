// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { X } from '~/shapes'

// local
// hooks
import { useSetFocus } from './useSetFocus'
import { useSetPixelPath } from '../../viz/useSetPixelPath'
// components
import { Button } from './button'


// remove this point from the path
export const Delete = ({ idx }) => {
    // get the path mutator that can delete a point
    const { remove } = useSetPixelPath()
    // and make a handler that clears the focus if my client happens to be in focus
    const { clear } = useSetFocus(idx)

    // build the handler
    const handler = () => {
        // remove the node from the path
        remove(idx)
        // clear the focus, iff necessary
        clear()
        // all done
        return
    }
    // assemble the behaviors
    const behaviors = {
        onClick: handler,
    }

    // render
    return (
        <Button {...behaviors}>
            <X />
        </Button>
    )
}


// end of file
