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


// the ticks at the edges of the bins, labeled at the ends and in the middle
export const Ticks = () => {
    // get the geometry
    const { counts, domain, left, bin, base, height, format, ticks } = useConfig()
    // a compact histogram has no ticks
    if (!ticks) {
        // so there is nothing to draw
        return null
    }
    // the number of bins
    const bins = counts.length
    // the edges that get a label: the two ends and the middle
    const labeled = new Set([0, Math.floor(bins / 2), bins])
    // the width of a bin in the units of the domain
    const step = (domain[1] - domain[0]) / Math.max(1, bins)
    // render
    return (
        <g>
            {Array.from({ length: bins + 1 }, (_, edge) => (
                <g key={edge}>
                    <path d={`M ${left + edge * bin} ${base} l 0 3`} style={styles.tick} />
                    {labeled.has(edge) &&
                        <text x={left + edge * bin} y={height - 2} style={styles.label}
                            textAnchor={edge === 0 ? "start" : edge === bins ? "end" : "middle"}
                        >
                            {format(domain[0] + edge * step)}
                        </text>
                    }
                </g>
            ))}
        </g>
    )
}


// end of file
