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
import { useGetZoomLevel } from '../../viz/useGetZoomLevel'
import { useSetFocus } from './useSetFocus'
// components
import { Button } from './button'


// locate the given point on the viewport
export const Focus = ({ idx, point }) => {
    // get the zoom level of the active viewport
    const zoom = useGetZoomLevel()
    // the handler that centers the active viewport
    const center = useCenterViewport()
    // and the {focus} mutator
    const { focus } = useSetFocus(idx)

    // turn the zoom level into a scale
    const scale = 2 ** zoom

    // wrap it in a control
    const activate = () => {
        // mark me as the focused one
        focus()
        // center the viewport on my point
        center({ x: point[0] / scale, y: point[1] / scale })
        // and done
        return
    }

    // assemble my behaviors
    const behaviors = {
        onClick: activate,
    }

    // render
    return (
        <Button {...behaviors}>
            <Target />
        </Button>
    )
}


// end of file
