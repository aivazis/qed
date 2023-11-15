// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// mark a point
export const Labels = ({ positions, values }) => {
    // check whether there are any labels to render
    if (positions.length === 0) {
        // and if not, bail
        return null
    }
    // otherwise, go through the selection and put a label below each node
    return (
        <g>
            {positions.map((position, idx) => {
                // get the position of the marker
                const [y, x] = position
                // get the value
                const [dataY, dataX] = values[idx]
                // use the value to make a key
                const key = `${dataY}x${dataX}`
                // and render
                return (
                    <g key={key}>
                        <Mat x={x} y={y + 35}>
                            {dataY} &#x2715; {dataX}
                        </Mat>
                        <Value x={x} y={y + 35}>
                            {dataY} &#x2715; {dataX}
                        </Value>
                    </g>
                )
            })}
        </g>
    )
}


// individual labels
// the placemat
const Mat = styled.text`
            font-family: inconsolata;
            font-size: 14px;
            text-anchor: middle;
            fill: none;
            stroke: hsl(0deg, 0%, 10%);
            stroke-width: 8;
            `

// the value
const Value = styled.text`
            font-family: inconsolata;
            font-size: 14px;
            text-anchor: middle;
            cursor: default;
            stroke: none;
            fill: hsl(28deg, 90%, 35%);
            `


// end of file
