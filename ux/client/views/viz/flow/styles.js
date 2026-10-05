// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// get the base styles
import base from '~/views/styles'


// publish
export default {
    // the container
    panel: {
        // inherit
        ...base.panel,
    },

    // the attributes of the canvas
    canvas: {
        // occupy all available space
        width: "100%",
        height: "100%",
    },

    // the paint of the canvas
    surface: {
        // dragging across the diagram moves things around; it must not sweep the labels into a
        // text selection; cancelling the mouse down instead would also keep the panel from
        // taking the focus the camera needs for its keys
        userSelect: "none",
        // webkit computes the standard property but still honors only its own
        WebkitUserSelect: "none",
    },

    cell: {
        // stroke
        stroke: "hsl(0deg, 0%, 15%)",
        strokeWidth: "1",
        vectorEffect: "non-scaling-stroke",
        // fill
        fill: "none",
    },

    spot: {
        // stroke
        stroke: "none",
        vectorEffect: "non-scaling-stroke",
        // fill
        fill: "url(#gridGlow)",
    },

    // the rings that tell what dropping a dragged node would do
    drop: {
        // merge with the node under it
        merge: {
            fill: "none",
            stroke: "hsl(200deg, 80%, 55%)",
            strokeWidth: 2,
            vectorEffect: "non-scaling-stroke",
            pointerEvents: "none",
        },
        // be sent back, since the spot is taken
        blocked: {
            fill: "none",
            stroke: theme.page.danger,
            strokeWidth: 2,
            vectorEffect: "non-scaling-stroke",
            pointerEvents: "none",
        },
    },

    // the connector lines
    connector: {
        // stroke
        stroke: "hsl(0deg, 0%, 35%)",
        strokeWidth: 2,
        vectorEffect: "non-scaling-stroke",
        // fill
        fill: "none",
    },

    // labels
    labels: {
        product: {
            fontFamily: "inconsolata",
            fontSize: 0.65,
            stroke: "none",
            fill: "hsl(200deg, 80%, 35%)",
            textAnchor: "middle",
            vectorEffect: "non-scaling-stroke",
        },

        factory: {
            fontFamily: "noto-italic",
            fontSize: 0.65,
            stroke: "none",
            fill: "hsl(28deg, 70%, 55%)",
            textAnchor: "middle",
            vectorEffect: "non-scaling-stroke",
        },

        input: {
            fontFamily: "inconsolata",
            fontSize: 0.5,
            stroke: "none",
            fill: "hsl(0deg, 0%, 35%)",
            textAnchor: "start",
            vectorEffect: "non-scaling-stroke",
        },

        output: {
            fontFamily: "inconsolata",
            fontSize: 0.5,
            stroke: "none",
            fill: "hsl(0deg, 0%, 35%)",
            textAnchor: "end",
            vectorEffect: "non-scaling-stroke",
        },
    }
}


// end of file
