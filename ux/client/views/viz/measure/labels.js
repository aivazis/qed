// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// components
import { Label } from './label'

// the set of anchor labels
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
                const [dataY, dataX] = values[idx].map(value => Math.trunc(value))
                // use the value to make a key
                const key = `${dataY}x${dataX}`
                // and render
                return (
                    <Label key={key} position={position} value={[dataY, dataX]} />
                )
            })}
        </g>
    )
}



// end of file
