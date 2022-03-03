// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// local
// hooks
import { useSelection } from './useSelection'
import { useSetSelection } from './useSetSelection'


// mark a point
export const Mark = ({ idx, at }) => {
    // grab the current selection
    const selection = useSelection()
    // get the selection handler factory
    const setSelection = useSetSelection(idx)

    // deduce my state
    const selected = selection.has(idx)
    // and use it to pick a capture
    const Highlight = selected ? SelectedHighlight : EnabledHighlight

    // make a handler that marks me as the selected one when i'm clicked
    const select = evt => {
        // don't let this bubble up; the parent's handler adds points...
        evt.stopPropagation()
        // and disable the default behavior
        evt.preventDefault()
        // select me
        setSelection()
        // all done
        return
    }

    // build my controller
    const behaviors = {
        onClick: select,
    }

    // render
    return (
        <g transform={`translate(${at[0]} ${at[1]})`} {...behaviors}>
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
