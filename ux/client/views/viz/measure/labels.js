// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// mark a point
export const Labels = ({ positions, values, selection }) => {
    // check whether there are any labels to render
    if (selection.length === 0) {
        // and if not, bail
        return null
    }
    // otherwise, go through the selection and put a label below each node
    return (
        <g>
            {selection.map(idx => {
                // get the position of the marker
                const [x, y] = positions[idx]
                // get the value
                const [dataX, dataY] = values[idx]
                // use the value to make a key
                const key = `${dataX} x ${dataY}`
                // and render
                return (
                    <Value key={key} x={x} y={y + 30}>
                        {x}&middot;{y}
                    </Value>
                )

            })}
        </g>
    )
}


// individual labels
const Value = styled.text`
    font-family: inconsolata;
    font-size: 20px;
    text-anchor: middle;
    cursor: default;
    stroke: none;
    fill: hsl(28deg, 90%, 55%);
`


// end of file
