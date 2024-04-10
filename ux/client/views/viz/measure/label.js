// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"

// mark a point
export const Label = ({ position, value }) => {
    // make a ref for the text
    const label = React.useRef(null)
    // and another for the mat
    const mat = React.useRef(null)

    // set up a layout effect to size the mat
    React.useLayoutEffect(() => {
        // get the label bounding box
        const box = label.current.getBBox()
        // adjust the mat
        mat.current.setAttribute("x", Math.round(box.x) - 5)
        mat.current.setAttribute("y", Math.round(box.y) - 5)
        mat.current.setAttribute("width", Math.round(box.width) + 10)
        mat.current.setAttribute("height", Math.round(box.height) + 10)
        // all done
        return
    })

    // get the position of the marker
    const { x, y } = position
    // get the value; we show: line x sample
    const { dataX, dataY } = value
    // and render
    return (
        <g>
            <Mat ref={mat} />
            <Value ref={label} x={x} y={y + 40}>
                {dataY} &#x2715; {dataX}
            </Value>
        </g>
    )
}


// individual labels
// the placemat
const Mat = styled.rect`
    fill: ${() => theme.page.relief};
    fill-opacity: 0.95;
    stroke: ${() => theme.page.selected};
`

// the value
const Value = styled.text`
    font-family: inconsolata;
    font-size: 14px;
    text-anchor: middle;
    cursor: default;
    stroke: none;
    fill: ${() => theme.page.highlight};
    fill-opacity: 0.70;
`


// end of file
