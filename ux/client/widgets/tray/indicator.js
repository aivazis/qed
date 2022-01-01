// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
import { Chevron } from '~/shapes'


// the tray state indicator
export const Indicator = ({ expanded, size = 16 }) => {
    // build the transform
    const xform = `scale(${size / 1000}) rotate(${expanded ? 90 : 0} 500 500)`

    // paint me
    return (
        <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
            width={size} height={size} >
            <g transform={xform}>
                <Chevron />
            </g>
        </svg>
    )
}


// end of file
