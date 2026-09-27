// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'


// the context: the configuration of the histogram and the geometry derived from it
export const Context = React.createContext(
    // the default value clients see when outside a provider
    {
        // the counts, one per bin
        counts: [],
        // the edges of the range the bins cover
        domain: [0, 1],
        // the size of the drawing, in pixels
        width: 240,
        height: 80,
    }
)


// the provider
export const Provider = ({ config, children }) => {
    // unpack the configuration, filling in what the client left out
    const {
        counts, domain = [0, 1], width = 240, height = 80, log = false,
        label = null, marker = null, format = edge => `${Math.round(100 * edge)}%`,
        ticks = true,
    } = config
    // the room below the bars for the tick labels, if there are any, and above them for the
    // tallest count
    const gutter = ticks ? 14 : 2
    const headroom = 4
    // the height of the bars at their tallest
    const reach = height - gutter - headroom
    // the width of a bin
    const bin = counts.length > 0 ? width / counts.length : width
    // the tallest bin sets the scale
    const tallest = Math.max(0, ...counts)
    // the scale: linear, or logarithmic so a dominant bin does not flatten the rest
    const scale = count => tallest === 0 ? 0 : log
        ? reach * Math.log1p(count) / Math.log1p(tallest)
        : reach * count / tallest
    // the extent of the domain
    const span = domain[1] - domain[0]
    // the position of a value of the domain along the axis; a domain of a single value puts
    // everything in the middle
    const at = value => span > 0 ? width * (value - domain[0]) / span : width / 2
    // the baseline
    const base = headroom + reach
    // assemble
    const value = {
        counts, domain, width, height, log, label, marker, format, ticks,
        gutter, headroom, reach, bin, tallest, scale, at, base,
    }
    // provide
    return (
        <Context.Provider value={value}>
            {children}
        </Context.Provider>
    )
}


// end of file
