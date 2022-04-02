// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// shapes
import { Target } from '~/shapes'
// styles
import { theme } from '~/palette'

// local
// hooks
import { useCenterViewport } from '../../../viz/useCenterViewport'
import { useGetZoomLevel } from '../../../viz/useGetZoomLevel'
import { usePixelPathSelection } from '../../../viz/usePixelPathSelection'
import { useSetPixelPathSelection } from '../../../viz/useSetPixelPathSelection'
// components
import { Button } from './button'


// locate the given point on the viewport
export const Focus = ({ idx, point }) => {
    // get the zoom level of the active viewport
    const zoom = useGetZoomLevel()
    // the handler that centers the active viewport
    const center = useCenterViewport()
    // the current point selection
    const selection = usePixelPathSelection()
    // and build a handler that selects nodes in single node mode
    const { selectContiguous, toggle, toggleMultinode } = useSetPixelPathSelection()

    // deduce my state
    const selected = selection.has(idx)
    // turn the zoom level into a scale
    const scale = 2 ** zoom

    // when clicked
    const focus = evt => {
        // don't let this bubble up
        evt.stopPropagation()

        // check the status of the modifiers
        const { ctrlKey, shiftKey } = evt

        // if there is no modifier present
        if (!ctrlKey && !shiftKey) {
            // select me in single node mode
            toggle(idx)
            // and center the viewport on my point
            center({ x: point[1] / scale, y: point[0] / scale })
            // done
            return
        }

        // if <ctrl> is present
        if (ctrlKey) {
            // toggle me in multinode mode
            toggleMultinode(idx)
            // done
            return
        }

        // if <shift> is present
        if (shiftKey) {
            // pick a range of nodes
            selectContiguous(idx)
            // done
            return
        }

        // and done
        return
    }

    // assemble my behaviors
    const behaviors = {
        onClick: focus,
    }

    // mix paint for my shape
    const paint = {
        icon: {
            stroke: selected ? theme.page.name : "hsl(0deg, 0%, 60%)",
        },
    }

    // render
    return (
        <Control behaviors={behaviors}>
            <Target style={paint} />
        </Control>
    )
}


// style me
const Control = styled(Button)`
    width: 1.5rem;
    text-align: end;
`


// end of file
