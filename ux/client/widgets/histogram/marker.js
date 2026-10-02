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


// an optional marker at a value of the domain, e.g. where one raster falls among many
export const Marker = () => {
    // get the geometry
    const { marker, at, width, left, headroom, base } = useConfig()
    // without a marker
    if (marker === null || marker === undefined) {
        // there is nothing to draw
        return null
    }
    // the position of the marker, kept on the drawing
    const x = Math.min(Math.max(at(marker.value), left + 1), width - 1)
    // render
    return (
        <g data-qed-marker={marker.value}>
            <path d={`M ${x} ${headroom} L ${x} ${base}`} style={styles.marker} />
            <title>{marker.label ?? `${marker.value}`}</title>
        </g>
    )
}


// end of file
