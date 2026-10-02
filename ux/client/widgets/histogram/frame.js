// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useConfig } from './useConfig'
// styles
import styles from './styles'


// the baseline under the bars
export const Frame = () => {
    // get the geometry
    const { width, left, base } = useConfig()
    // render
    return (
        <path d={`M ${left} ${base} L ${width} ${base}`} style={styles.frame} />
    )
}


// end of file
