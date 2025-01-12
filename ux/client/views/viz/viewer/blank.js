// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// project
// shapes
import { Data as Icon } from '~/shapes'

// locals
// styles
import styles from './styles'


// the area
export const Blank = ({ behaviors }) => {
    // grab the style
    const { blank } = styles
    // render
    return (
        <section style={blank.placeholder} {...behaviors} >
            <svg style={blank.icon} version="1.1" xmlns="http://www.w3.org/2000/svg">
                <g transform="scale(0.3)" fill="#f37f19" stroke="none">
                    <Icon style={blank.shape} />
                </g>
            </svg>
        </section>
    )
}


// end of file
