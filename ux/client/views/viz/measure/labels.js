// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


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
                const [sample, line] = position
                // get the value
                const [dataSample, dataLine] = values[idx]
                // use the value to make a key
                const key = `${dataSample} x ${dataLine}`
                // and render
                return (
                    <Value key={key} x={sample} y={line + 35}>
                        {dataLine} &#x2715; {dataSample}
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
    fill: hsl(28deg, 90%, 35%);
`


// end of file
