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


// the bars, one per bin
export const Bars = () => {
    // get the geometry
    const { counts, domain, left, bin, scale, base, format } = useConfig()
    // the width of a bin in the units of the domain
    const step = (domain[1] - domain[0]) / Math.max(1, counts.length)
    // render
    return (
        <g>
            {counts.map((count, index) => {
                // the height of this bar
                const tall = scale(count)
                // the edges of its bin, as the client spells them
                const low = format(domain[0] + index * step)
                const high = format(domain[0] + (index + 1) * step)
                // draw it, with a hair of room on either side
                return (
                    <rect key={index}
                        x={left + index * bin + 0.5} y={base - tall}
                        width={Math.max(0, bin - 1)} height={tall}
                        style={styles.bar}
                        data-qed-bin={index} data-qed-count={count}
                    >
                        <title>{`${low}-${high}: ${count}`}</title>
                    </rect>
                )
            })}
        </g>
    )
}


// end of file
