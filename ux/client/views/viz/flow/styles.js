// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// get the base styles
import base from '~/views/styles'


// the solid pucks of factories, in the color of factories
const isoFactory = {
    top: { fill: "hsl(28deg, 70%, 45%)", stroke: "hsl(28deg, 70%, 60%)", strokeWidth: 1, vectorEffect: "non-scaling-stroke" },
    side: { fill: "hsl(28deg, 70%, 26%)", stroke: "hsl(28deg, 70%, 40%)", strokeWidth: 1, vectorEffect: "non-scaling-stroke" },
    band: { fill: "hsl(28deg, 70%, 26%)", stroke: "none" },
    highlight: { fill: "none", stroke: "hsl(28deg, 40%, 80%)", strokeWidth: 2, vectorEffect: "non-scaling-stroke" },
}

// and of products, in the color of products
const isoProduct = {
    top: { fill: "hsl(200deg, 80%, 38%)", stroke: "hsl(200deg, 80%, 55%)", strokeWidth: 1, vectorEffect: "non-scaling-stroke" },
    side: { fill: "hsl(200deg, 80%, 20%)", stroke: "hsl(200deg, 80%, 35%)", strokeWidth: 1, vectorEffect: "non-scaling-stroke" },
    band: { fill: "hsl(200deg, 80%, 20%)", stroke: "none" },
    highlight: { fill: "none", stroke: "hsl(200deg, 40%, 75%)", strokeWidth: 2, vectorEffect: "non-scaling-stroke" },
}

// the paint of a puck by how far down its node is pinned, made from the {solid} paint of an
// instance: a protocol is a dashed outline filled with the paint of the page, so it hides what is
// behind it and can be picked up anywhere, and a class is tinted, its {top} and {side} darker
const isoLevels = ({ solid, top, side }) => ({
    // an outline
    protocol: {
        top: { ...solid.top, fill: theme.page.background, strokeDasharray: "3 2" },
        side: { ...solid.side, fill: theme.page.background, strokeDasharray: "3 2" },
        band: { ...solid.band, fill: theme.page.background },
        highlight: solid.highlight,
    },
    // a tint
    class: {
        top: { ...solid.top, fill: top },
        side: { ...solid.side, fill: side },
        band: { ...solid.band, fill: side },
        highlight: solid.highlight,
    },
    // solid
    instance: solid,
})


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

    // the isometric view
    iso: {
        // the lattice on the floor
        floor: {
            stroke: "hsl(0deg, 0%, 14%)",
            strokeWidth: 1,
            vectorEffect: "non-scaling-stroke",
            fill: "none",
        },
        // the cell under the cursor
        cell: {
            stroke: "hsl(0deg, 0%, 30%)",
            strokeWidth: 1,
            vectorEffect: "non-scaling-stroke",
            fill: "hsl(0deg, 0%, 10%)",
        },
        // the stalk from a node above the floor down to its footprint
        stalk: {
            stroke: "hsl(0deg, 0%, 40%)",
            strokeWidth: 1,
            strokeDasharray: "2 3",
            vectorEffect: "non-scaling-stroke",
            fill: "none",
        },
        // the leader from a factory up to its name: like a stalk, but dimmer, and in the color
        // of the factory, so it ties the name to its solid without competing with the connectors
        leader: {
            stroke: "hsl(28deg, 45%, 40%)",
            strokeWidth: 1,
            strokeDasharray: "1 2",
            vectorEffect: "non-scaling-stroke",
            fill: "none",
        },
        // and the footprint
        footprint: {
            stroke: "hsl(0deg, 0%, 30%)",
            strokeWidth: 1,
            vectorEffect: "non-scaling-stroke",
            fill: "hsla(0deg, 0%, 0%, 0.35)",
        },
        // factories, as pucks in the color of factories
        factory: isoFactory,
        // slots without a product
        slot: {
            top: { fill: "hsl(0deg, 0%, 32%)", stroke: "hsl(0deg, 0%, 45%)", strokeWidth: 1, vectorEffect: "non-scaling-stroke" },
            side: { fill: "hsl(0deg, 0%, 17%)", stroke: "hsl(0deg, 0%, 35%)", strokeWidth: 1, vectorEffect: "non-scaling-stroke" },
            band: { fill: "hsl(0deg, 0%, 17%)", stroke: "none" },
            highlight: { fill: "none", stroke: "hsl(0deg, 0%, 70%)", strokeWidth: 2, vectorEffect: "non-scaling-stroke" },
        },
        // and with one
        product: isoProduct,
    },

    // the paint of the pucks, by how far down their node is pinned
    isoLevels: {
        // factories
        factory: isoLevels({ solid: isoFactory, top: "hsl(28deg, 70%, 25%)", side: "hsl(28deg, 70%, 15%)" }),
        // products
        product: isoLevels({ solid: isoProduct, top: "hsl(200deg, 80%, 15%)", side: "hsl(200deg, 80%, 10%)" }),
    },

    // the paint of the flat glyphs, by how far down their node is pinned: a protocol is an
    // outline, a class is tinted, and an instance is solid; an outline is filled with the paint
    // of the page, rather than with nothing, so it hides what runs behind it and can still be
    // picked up anywhere inside it
    levels: {
        // factories, in the color of factories
        factory: {
            protocol: { icon: { fill: theme.page.background, strokeDasharray: "3 2" } },
            class: { icon: { fill: "hsl(28deg, 70%, 25%)" } },
            instance: { icon: { fill: "hsl(28deg, 70%, 45%)" } },
        },
        // products, in the color of products
        product: {
            protocol: { icon: { fill: theme.page.background, strokeDasharray: "3 2" } },
            class: { icon: { fill: "hsl(200deg, 80%, 15%)" } },
            instance: { icon: { fill: "hsl(200deg, 80%, 35%)" } },
        },
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
