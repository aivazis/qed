// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay'
import styled from 'styled-components'

// project
// shapes
import { Target } from '~/shapes'
// styles
import { theme } from '~/palette'

// project
// hooks
import { useCenterViewport } from '~/views/viz'

// local
// hooks
import { useSetPixelPathSelection } from '../../../../main/useSetPixelPathSelection'
// components
import { Button } from './button'
import { useAnchorExtendSelection } from '~/views/viz/measure'
import { useAnchorToggleSelection } from '~/views/viz/measure'
import { useAnchorToggleSelectionMulti } from '~/views/viz/measure'


// locate the given point on the viewport
export const Focus = ({ viewport, view, idx, point }) => {
    // unpack the view
    const { measure, zoom } = useFragment(focusMeasureGetMeasureLayerFragment, view)
    // the handler that centers the active viewport
    const center = useCenterViewport()
    // and build a handlers for the various selection modes
    const { select } = useAnchorExtendSelection(viewport)
    const { toggle } = useAnchorToggleSelection(viewport)
    const { toggle: toggleMultinode } = useAnchorToggleSelectionMulti(viewport)

    // get the current anchor selection
    const { selection } = measure

    // deduce my state
    const selected = selection.includes(idx)
    // turn the zoom level into a scale
    const scale = [2 ** -zoom.vertical, 2 ** -zoom.horizontal]

    // when clicked
    const focus = evt => {
        // don't let this bubble up
        evt.stopPropagation()

        // check the status of the modifiers
        const { altKey, shiftKey } = evt

        // if there is no modifier present
        if (!altKey && !shiftKey) {
            // select me in single node mode
            toggle(idx)
            // and center the viewport on my point
            center({ x: point[1] / scale[1], y: point[0] / scale[0] })
            // done
            return
        }

        // if <ctrl> is present
        if (altKey) {
            // toggle me in multinode mode
            toggleMultinode(idx)
            // done
            return
        }

        // if <shift> is present
        if (shiftKey) {
            // pick a range of nodes
            select(idx)
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
            stroke: selected ? theme.page.name : theme.page.bright,
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


// the fragment
const focusMeasureGetMeasureLayerFragment = graphql`
    fragment focusMeasureGetMeasureLayerFragment on View {
        measure {
            selection
        }
        zoom {
            horizontal
            vertical
        }
    }
`


// end of file
