// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// an invisible rectangle behind a label that catches the pointer over the label's whole box and
// some slack around it, so the label is an easier target than its text alone. it also gives the
// group that holds the pair an extent that browser automation can aim at: when driving webkit,
// playwright places a positioned svg text at the origin of its coordinate system, so a click
// aimed at the text lands elsewhere, while a group or a rectangle is placed correctly. the
// label is centered on ({x}, {y}) with its baseline at {y}, {text} is what it shows, and
// {fontSize} is its size in intrinsic units
export const Hitbox = ({ x, y, text, fontSize }) => {
    // a monospace glyph advances about half an em; add half an em of slack on each side
    const width = (0.55 * text.length + 1) * fontSize
    // the box covers the ascenders and a bit of descender
    const height = 1.2 * fontSize
    // render
    return (
        <Box x={x - width / 2} y={y - 0.9 * fontSize} width={width} height={height} />
    )
}


// styling
const Box = styled.rect`
    fill: none;
    stroke: none;
    pointer-events: all;

    /* a click on a label sets the value */
    & {
        cursor: pointer;
    }

    /* except on an editable end, where a double click edits it */
    [data-pyre-widget-part="bound"] > & {
        cursor: text;
    }
`


// end of file
