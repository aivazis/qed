// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"

// locals
// styles
import styles from './styles'


// the zoom controller
export const Controller = () => {

    // mix my paint
    const paint = styles.controller

    const indicator = <path d="M 0 0 l -30 -50 l 60 0 z" style={paint.indicator} />

    // render
    return (
        <>
            <path d="M 100 225 l 0 50" style={paint.tick} />
            <path d="M 300 225 l 0 50" style={paint.tick} />
            <path d="M 500 225 l 0 50" style={paint.tick} />
            <path d="M 700 225 l 0 50" style={paint.tick} />
            <path d="M 900 225 l 0 50" style={paint.tick} />
            <path d="M 0 250 L 1000 250" style={paint.axis} />
            <text x="100" y="350" style={paint.label}>0</text>
            <text x="300" y="350" style={paint.label}>1</text>
            <text x="500" y="350" style={paint.label}>2</text>
            <text x="700" y="350" style={paint.label}>3</text>
            <text x="900" y="350" style={paint.label}>4</text>
            <g transform="translate(500 185)">
                {indicator}
            </g>
        </>
    )
}


// end of file
