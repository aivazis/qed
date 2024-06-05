// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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

    canvas: {
        // occupy all available space
        width: "100%",
        height: "100%",
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
            fontFamily: "noto",
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
