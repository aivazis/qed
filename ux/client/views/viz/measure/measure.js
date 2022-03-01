// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// styles
import styles from './styles'


// the layer
export const Measure = ({ raster }) => {
    // mix my paint
    const paint = styles.measure(raster)
    // controllers
    const behaviors = {
        onClick: () => console.log('click')
    }
    // render
    return (
        <div style={paint} {...behaviors} >
            hello
        </div>
    )
}


// end of file
