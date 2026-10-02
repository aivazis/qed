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


// render a count compactly
const compact = count => count >= 1e6
    ? `${count / 1e6}M` : count >= 1e3 ? `${count / 1e3}k` : `${count}`


// the counts worth a tick: the powers of ten on a logarithmic scale, and on a linear one the
// multiples of the round step that divides the tallest count into a few parts
const marks = (tallest, log) => {
    // an empty histogram
    if (tallest <= 0) {
        // has nothing but its baseline
        return [0]
    }
    // on a logarithmic scale
    if (log) {
        // every power of ten up to the tallest
        const powers = [0]
        for (let power = 1; power <= tallest; power *= 10) {
            // gets a tick
            powers.push(power)
        }
        // hand them off
        return powers
    }
    // on a linear one, the raw step that makes about three parts
    const raw = tallest / 3
    // its order of magnitude
    const magnitude = 10 ** Math.floor(Math.log10(raw))
    // the round step: one, two, or five times it
    const step = [1, 2, 5, 10].map(factor => factor * magnitude).find(step => step >= raw)
    // the multiples of the step up to the tallest
    return Array.from({ length: Math.floor(tallest / step) + 1 }, (_, index) => index * step)
}


// add the tallest count to the {ticks}, unless the last one is too close to it to tell apart, so
// the height of the tallest bar can always be read off the axis
const labeled = (ticks, tallest, scale) => {
    // the last tick
    const last = ticks[ticks.length - 1]
    // far enough below the tallest bar
    if (last < tallest && scale(tallest) - scale(last) > 8) {
        // gets company
        return [...ticks, tallest]
    }
    // otherwise, the ticks are enough
    return ticks
}


// the vertical axis: the counts along the left edge of the bars, and what they count
export const Axis = () => {
    // get the geometry
    const { ticks, unit, log, tallest, scale, left, headroom, base } = useConfig()
    // a compact histogram has no axis
    if (!ticks) {
        // so there is nothing to draw
        return null
    }
    // render
    return (
        <g>
            {/* the axis */}
            <path d={`M ${left} ${headroom} L ${left} ${base}`} style={styles.frame} />
            {/* the ticks and their counts */}
            {labeled(marks(tallest, log), tallest, scale).map(count => {
                // the height of the tick
                const y = base - scale(count)
                // render
                return (
                    <g key={count}>
                        <path d={`M ${left - 3} ${y} l 3 0`} style={styles.tick} />
                        <text x={left - 5} y={y + 3} textAnchor="end" style={styles.label}>
                            {compact(count)}
                        </text>
                    </g>
                )
            })}
            {/* what is counted */}
            {unit &&
                <text x={left + 3} y={headroom - 3} style={styles.label}>
                    {log ? `${unit}, log scale` : unit}
                </text>
            }
        </g>
    )
}


// end of file
