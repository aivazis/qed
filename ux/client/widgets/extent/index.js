// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
// project
import { useResizeObserver } from '~/hooks'
// locals
import styles from './styles'


// a box that knows its size
export const Extent = ({ behaviors, style }) => {
    // get my extent
    const { ref, extent } = useResizeObserver()
    // mix my styles
    const extentStyle = { ...styles, ...style }
    // and paint me
    return (
        <div ref={ref} style={extentStyle} {...behaviors} >
            extent: {extent.width} x {extent.height}
        </div>
    )
}


// end of file
