// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

//project
// hooks
import { useEvent } from '~/hooks'

// local
// hooks
import { usePixelPathSelection } from '../viz/usePixelPathSelection'
import { useSetPixelPathSelection } from '../viz/useSetPixelPathSelection'
import { useStartMoving } from './useStartMoving'
import { useStopMoving } from './useStopMoving'


// mark a point
export const Mark = ({ viewport, idx, at }) => {
    // make a ref for my client area
    const me = React.useRef(null)

    // grab the moving flag mutators
    const startMoving = useStartMoving(idx)
    const stopMoving = useStopMoving()
    // grab the current selection
    const selection = usePixelPathSelection(viewport)
    // get the selection handler factory
    const { selectContiguous, toggle, toggleMultinode } = useSetPixelPathSelection(viewport)

    // deduce my state
    const selected = selection.has(idx)
    // and use it to pick a capture
    const Highlight = selected ? SelectedHighlight : EnabledHighlight


    // movement
    const move = () => {
        // mark me as the initiator of the move
        startMoving()
        // all done
        return
    }

    // mark selection
    const pick = evt => {
        // don't let this bubble up
        evt.stopPropagation()

        // check the status of the modifiers
        const { ctrlKey, shiftKey } = evt

        // the mouse activity started and ended with me, so nobody is moving
        stopMoving()

        // if there is no modifier present
        if (!ctrlKey && !shiftKey) {
            // select me in single node mode
            toggle(idx)
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

        // all done
        return
    }

    // mouse event listeners
    // when the user clicks in my area
    useEvent({
        name: "click", listener: pick, client: me,
        triggers: [toggle, selectContiguous]
    })

    // when the mouse button is pressed in my area
    useEvent({
        name: "mousedown", listener: move, client: me,
        triggers: [startMoving]
    })

    // render
    return (
        <g ref={me} transform={`translate(${at[1]} ${at[0]})`}>
            <Mat cx={0} cy={0} r="15" />
            <Ring cx={0} cy={0} r="7" />
            <Crosshairs d={crosshairs} />
            <Highlight cx={0} cy={0} r="12" />
        </g>
    )
}


// placemat
const Mat = styled.circle`
    fill: hsl(0deg, 0%, 10%, 0.75);
    stroke: none;
`


// the event capture area
const EnabledHighlight = styled.circle`
    & {
        fill: hsl(0deg, 0%, 0%, 0);
        stroke: none;
        cursor: pointer;
    }

    &:hover {
        stroke: hsl(28deg, 90%, 55%);
        stroke-width: 1;
    }

    &:active {
        stroke: hsl(28deg, 90%, 55%);
        stroke-width: 1;
    }
`

// a selected node has a special capture
const SelectedHighlight = styled.circle`
    fill: hsl(0deg, 0%, 0%, 0);
    stroke: hsl(28deg, 90%, 35%);
    stroke-width: 2;
    cursor: pointer;
`

// node
const Ring = styled.circle`
    fill: none;
    stroke: hsl(28deg, 90%, 55%);
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
    stroke: hsl(28deg, 90%, 55%);
    stroke-width: 1;
    vector-effect: non-scaling-stroke;
`


// end of file
