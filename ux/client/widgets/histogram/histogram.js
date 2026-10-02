// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { SVG } from '../svg'

// locals
// context
import { Provider } from './context'
// hooks
import { useConfig } from './useConfig'
// components
import { Axis } from './axis'
import { Bars } from './bars'
import { Frame } from './frame'
import { Marker } from './marker'
import { Ticks } from './ticks'


// a histogram: bars over bins of equal width that cover a {domain}, with an optional marker
export const Histogram = ({ ...config }) => {
    // set up my context and draw
    return (
        <Provider config={config}>
            <Drawing />
        </Provider>
    )
}


// lay out the drawing
const Drawing = () => {
    // get what i need
    const { counts, width, height, label } = useConfig()
    // the summary a screen reader announces in place of the picture
    const summary = `${label ?? "histogram"}: ${counts.join(", ")}`
    // render; the frame and the ticks are decoration, the bars carry the counts
    return (
        <SVG width={width} height={height} viewBox={`0 0 ${width} ${height}`}
            role="img" aria-label={summary} data-qed-widget="histogram"
        >
            <g aria-hidden="true">
                <Frame />
                <Axis />
                <Ticks />
            </g>
            <Bars />
            <Marker />
        </SVG>
    )
}


// end of file
