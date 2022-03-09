// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Target } from '~/shapes'

// local
// hooks
import { useCenterViewport } from '../../viz/useCenterViewport'
// components
import { Button } from './button'


// locate the given point on the viewport
export const Focus = ({ idx, point }) => {
    // get the handler that centers the active viewport
    const center = useCenterViewport()

    // wrap it in a control
    const centerAt = () => {
        // center the viewport on my point
        center({ x: point[0], y: point[1] })
        // and done
        return
    }

    // assemble my behaviors
    const behaviors = {
        onClick: centerAt,
    }

    // render
    return (
        <Button {...behaviors}>
            <Target />
        </Button>
    )
}


// end of file
