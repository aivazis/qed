// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
// shapes
import { Data } from '~/shapes'
// styles
import styles from './styles'


// the area
export const Blank = ({ behaviors }) => {
    // grab the style
    const { blank } = styles
    // render
    return (
        <section style={blank.nyi} {...behaviors} >
            <div style={blank.placeholder}>
                <svg style={blank.icon} version="1.1" xmlns="http://www.w3.org/2000/svg">
                    <g transform="scale(0.3)" fill="#f37f19" stroke="none">
                        <Data style={blank.shape} />
                    </g>
                </svg>
            </div>
        </section>
    )
}


// end of file
