// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// hooks
import { useEvent } from '~/hooks'
// colors
import { theme } from "~/palette"

// local
// hooks
import { useAnchorDrag } from './useAnchorDrag'
import { useAnchorExtendSelection } from './useAnchorExtendSelection'
import { useAnchorToggleSelection } from './useAnchorToggleSelection'
import { useAnchorToggleSelectionMulti } from './useAnchorToggleSelectionMulti'


// mark a point
export const Anchor = ({ viewport, selection, idx, at }) => {
    // make a ref for my client area
    const me = React.useRef(null)
    // record of the mouse position when the user clicks on me; this is used to detect
    // motion between mouse down and mouse up so that we can skip the selection toggles
    // when the mark is being moved around
    const [position, setPosition] = React.useState(null)
    // grab the moving flag mutator
    const { start } = useAnchorDrag()

    // get the selection mutators
    const { select } = useAnchorExtendSelection(viewport)
    const { toggle } = useAnchorToggleSelection(viewport)
    const { toggle: toggleMulti } = useAnchorToggleSelectionMulti(viewport)

    // deduce my state
    const selected = selection.includes(idx)
    // and use it to choose how to render the event capture area
    const Highlight = selected ? SelectedHighlight : EnabledHighlight

    // movement
    const move = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // record the mouse position
        setPosition({ x: evt.clientX, y: evt.clientY })
        // mark me as the initiator of the move
        start(idx)
        // all done
        return
    }

    // mark selection
    const pick = evt => {
        // N.B.:
        //     don't prevent this event from bubbling up when this handler is tied to {moveup};
        //     the parent depends on the event reaching it to terminate anchor dragging
        // if i've moved since clicked
        if (position.x !== evt.clientX || position.y != evt.clientY) {
            // do nothing
            return
        }
        // otherwise, grab the status of the modifiers
        const { altKey, shiftKey } = evt
        // if there is no modifier present
        if (!altKey && !shiftKey) {
            // select me in single node mode
            toggle(idx)
            // done
            return
        }
        // if <alt> is present
        if (altKey) {
            // toggle me in multinode mode
            toggleMulti(idx)
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
        // all done
        return
    }

    // mouse event listeners
    // when the user clicks in my area
    useEvent({
        name: "mouseup", listener: pick, client: me,
        triggers: [position, select, toggle, toggleMulti]
    })

    // when the mouse button is pressed in my area
    useEvent({
        name: "mousedown", listener: move, client: me,
        triggers: [start]
    })

    // render
    return (
        <g ref={me} transform={`translate(${at.x} ${at.y})`}>
            <Mat cx={0} cy={0} r="15" />
            <Ring cx={0} cy={0} r="7" />
            <Crosshairs d={crosshairs} />
            <Highlight cx={0} cy={0} r="12" />
        </g>
    )
}


// place mat
const Mat = styled.circle`
    fill: ${(() => theme.page.shaded)};
    stroke: none;
`


// the event capture area
const EnabledHighlight = styled.circle`
    & {
        fill: ${() => theme.page.transparent};
        stroke: none;
        cursor: pointer;
    }

    &:hover {
        stroke: ${() => theme.page.highlight};
        stroke-width: 1;
    }

    &:active {
        stroke: ${() => theme.page.highlight};
        stroke-width: 1;
    }
`

// a selected node has a special capture
const SelectedHighlight = styled.circle`
    fill: ${() => theme.page.transparent};
    stroke: ${() => theme.page.highlight};
    stroke-width: 2;
    cursor: pointer;
`

// node
const Ring = styled.circle`
    fill: none;
    stroke: ${() => theme.page.highlight};
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`

// the path data for the crosshairs
const crosshairs = `
        M -9 0 l 6 0
        M 0 -9 l 0 6
        M 9 0 l -6 0
        M 0 9 l 0 -6
    `

const Crosshairs = styled.path`
    fill: none;
    stroke: ${() => theme.page.highlight};
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`


// end of file
