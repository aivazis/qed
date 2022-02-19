// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// styles
import styles from './styles'


// export the SVG wrapper
export const SVG = ({ height, width, style, children, ...rest }) => {
    // mix my paint
    const paint = styles.svg(style)
    // and render
    return (
        <svg version="2.0" xmlns="http://www.w3.org/2000/svg"
            height={height} width={width} style={paint} {...rest}
        >
            {children}
        </svg>
    )
}


// end of file
