// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// get colors
import { theme } from '~/palette'


// the baseline
const frame = {
    fill: "none",
    stroke: theme.page.normal,
    strokeWidth: 1,
    vectorEffect: "non-scaling-stroke",
}

// the bars
const bar = {
    fill: theme.page.normal,
    stroke: "none",
}

// the ticks
const tick = {
    fill: "none",
    stroke: theme.page.dim,
    strokeWidth: 1,
    vectorEffect: "non-scaling-stroke",
}

// the tick labels
const label = {
    fill: theme.page.dim,
    fontFamily: "inconsolata",
    fontSize: "11px",
}

// the marker
const marker = {
    fill: "none",
    stroke: theme.page.highlight,
    strokeWidth: 2,
    vectorEffect: "non-scaling-stroke",
}


// publish
export default {
    frame,
    bar,
    tick,
    label,
    marker,
}


// end of file
