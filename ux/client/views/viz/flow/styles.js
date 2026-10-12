// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// get the base styles
import base from '~/views/styles'
// the paint of the terminals
import terminalPaint from '~/shapes/terminal/styles'
// and of the factories, whose highlight the fan borrows for its focus
import factoryPaint from '~/shapes/factory/styles'


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

// forest green, for the methods of factories
const forest = {
    ink: "hsl(120deg, 45%, 32%)",
    paint: "hsl(120deg, 45%, 13%)",
    glyph: "hsl(120deg, 45%, 50%)",
    name: "hsl(120deg, 30%, 40%)",
}

// the paint of a puck by how far down its node is pinned, made from the {solid} paint of an
// instance: a protocol is a dashed outline, a class is a solid one, and an instance is a solid
// outline around a darker {top} and {side}, so its border stays visible; an outline is filled with
// the paint of the page, rather than with nothing, so it hides what is behind it and can be picked
// up anywhere
const isoLevels = ({ solid, top, side }) => ({
    // a dashed outline
    protocol: {
        top: { ...solid.top, fill: theme.page.background, strokeDasharray: "3 2" },
        side: { ...solid.side, fill: theme.page.background, strokeDasharray: "3 2" },
        band: { ...solid.band, fill: theme.page.background },
        highlight: solid.highlight,
    },
    // a solid outline
    class: {
        top: { ...solid.top, fill: theme.page.background },
        side: { ...solid.side, fill: theme.page.background },
        band: { ...solid.band, fill: theme.page.background },
        highlight: solid.highlight,
    },
    // a solid outline around a darker fill
    instance: {
        top: { ...solid.top, fill: top },
        side: { ...solid.side, fill: side },
        band: { ...solid.band, fill: side },
        highlight: solid.highlight,
    },
})


// publish
export default {
    // the container
    panel: {
        // inherit
        ...base.panel,
        // the panel takes the focus only so its keys reach it; it is not in the tab order, and
        // the fan shows what the keys are doing, so the ring webkit draws around it once a key
        // is pressed is noise
        outline: "none",
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
        // the end of a factory that has no slots: a dark red puck with no outline, the way the
        // flat terminal is a disc, and the cross of the terminal on its cap
        terminal: {
            top: { fill: terminalPaint.decoration.fill, stroke: "none" },
            side: { fill: "hsl(0deg, 40%, 12%)", stroke: "none" },
            band: { fill: "hsl(0deg, 40%, 12%)", stroke: "none" },
            cross: terminalPaint.icon,
        },
    },

    // the paint of the pucks, by how far down their node is pinned
    isoLevels: {
        // factories
        factory: isoLevels({ solid: isoFactory, top: "hsl(28deg, 70%, 25%)", side: "hsl(28deg, 70%, 15%)" }),
        // products
        product: isoLevels({ solid: isoProduct, top: "hsl(200deg, 80%, 15%)", side: "hsl(200deg, 80%, 10%)" }),
    },

    // the paint of the flat glyphs, by how far down their node is pinned: a protocol is a dashed
    // outline, a class is a solid one, and an instance is a solid outline around a darker fill, the
    // way the shapes are drawn on their own; an outline is filled with the paint of the page,
    // rather than with nothing, so it hides what runs behind it and can still be picked up
    // anywhere inside it
    levels: {
        // factories, in the color of factories
        factory: {
            protocol: { icon: { fill: theme.page.background, strokeDasharray: "3 2" } },
            class: { icon: { fill: theme.page.background } },
            instance: { icon: { fill: "hsl(28deg, 70%, 25%)" } },
        },
        // products, in the color of products
        product: {
            protocol: { icon: { fill: theme.page.background, strokeDasharray: "3 2" } },
            class: { icon: { fill: theme.page.background } },
            instance: { icon: { fill: "hsl(200deg, 80%, 15%)" } },
        },
    },

    // the fan that offers the next level down of a factory around it
    // the fields over the canvas that change a setting or name an instance, styled the way the
    // forms of the app are
    inline: {
        // the holder, over the canvas, backed by the page so it hides what it covers
        box: {
            position: "absolute",
            zIndex: 10,
            padding: "0.1em 0.3em",
            backgroundColor: theme.page.background,
            fontSize: "13px",
        },
        // the prompt and the input, on one line
        row: {
            display: "flex",
            alignItems: "baseline",
            gap: "0.4em",
        },
        // what is asked for
        prompt: {
            fontFamily: "rubik-light",
            textTransform: "uppercase",
            color: "hsl(0deg, 0%, 55%)",
        },
        // the input, narrower than the forms', in the size of the text so it scales with it, and
        // so does its padding, which the placement of the field takes into account
        input: {
            width: "17em",
            padding: "0 0.3em",
        },
        // the values a setting might take, in a list below the field that scrolls past a handful
        suggestions: {
            // the holder
            box: {
                marginTop: "0.3em",
                borderTop: "1px solid hsl(0deg, 0%, 20%)",
                paddingTop: "0.2em",
            },
            // how many there are
            count: {
                fontFamily: "rubik-light",
                fontSize: "75%",
                textTransform: "uppercase",
                color: "hsl(0deg, 0%, 40%)",
                padding: "0 0.3em 0.2em 0.3em",
            },
            // the list, about nine rows tall before it scrolls
            list: {
                maxHeight: "12.6em",
                overflowY: "auto",
                // reaching either end of the list does not carry the scroll on to what is behind it
                overscrollBehavior: "contain",
                lineHeight: "1.4em",
                fontFamily: "inconsolata",
                color: "hsl(0deg, 0%, 70%)",
            },
            // a row
            row: {
                padding: "0 0.3em",
                whiteSpace: "nowrap",
                cursor: "pointer",
            },
            // the row the arrows or the pointer picked
            picked: {
                padding: "0 0.3em",
                whiteSpace: "nowrap",
                cursor: "pointer",
                backgroundColor: "hsl(0deg, 0%, 15%)",
            },
        },
        // the reason the last try was refused
        error: {
            maxWidth: "22em",
            paddingTop: "0.2em",
            fontFamily: "inconsolata",
            color: "hsl(0deg, 70%, 65%)",
        },
    },

    // what hangs below a factory: its traits, which are data, in the blue of products, and its
    // methods, in forest green
    settings: {
        // the stem that hangs from the hub of the factory
        stem: {
            stroke: "hsl(0deg, 0%, 40%)",
            strokeWidth: 1,
            vectorEffect: "non-scaling-stroke",
        },
        // the beads that fold the strings, by group
        expander: {
            // the patch of the page under the glyph
            patch: { fill: theme.page.background, stroke: "none" },
            traits: {
                glyph: { stroke: "hsl(200deg, 80%, 60%)", strokeWidth: 1.5, vectorEffect: "non-scaling-stroke" },
                label: { fontFamily: "inconsolata", fontSize: 0.45, stroke: "none", fill: "hsl(200deg, 50%, 45%)" },
            },
            methods: {
                glyph: { stroke: forest.glyph, strokeWidth: 1.5, vectorEffect: "non-scaling-stroke" },
                label: { fontFamily: "inconsolata", fontSize: 0.45, stroke: "none", fill: forest.name },
            },
        },
        // the bead of a trait: blank while the factory is a protocol or a class, whose traits are
        // a specification, and filled once it is an instance, whose traits hold values
        trait: {
            blank: { fill: theme.page.background, stroke: "hsl(200deg, 80%, 35%)", strokeWidth: 2, vectorEffect: "non-scaling-stroke" },
            instance: { fill: "hsl(200deg, 80%, 15%)", stroke: "hsl(200deg, 80%, 35%)", strokeWidth: 2, vectorEffect: "non-scaling-stroke" },
        },
        // the bead of a method, filled the same way, and its name
        method: {
            blank: { fill: theme.page.background, stroke: forest.ink, strokeWidth: 2, vectorEffect: "non-scaling-stroke" },
            instance: { fill: forest.paint, stroke: forest.ink, strokeWidth: 2, vectorEffect: "non-scaling-stroke" },
            name: { fontFamily: "inconsolata", fontSize: 0.45, stroke: "none", fill: forest.name },
        },
        // the name of a trait
        name: {
            fontFamily: "inconsolata",
            fontSize: 0.45,
            stroke: "none",
            fill: "hsl(200deg, 80%, 55%)",
        },
        // its value
        value: {
            fill: "hsl(0deg, 0%, 85%)",
        },
        // or that it has none
        unset: {
            fill: "hsl(0deg, 0%, 50%)",
            fontStyle: "italic",
        },
        // why a method failed
        failure: {
            fill: "hsl(0deg, 70%, 65%)",
        },
        // a bead that does something when clicked
        clickable: {
            cursor: "pointer",
        },
    },

    fan: {
        // a satellite, which is picked anywhere inside its ring
        satellite: {
            cursor: "pointer",
        },
        // the line from the factory to a satellite
        spoke: {
            stroke: "hsl(0deg, 0%, 40%)",
            strokeWidth: 1,
            vectorEffect: "non-scaling-stroke",
            opacity: 0.5,
        },
        // the invisible ring that catches the pointer
        ring: {
            fill: "transparent",
            stroke: "none",
        },
        // a new instance: a plus sign, in the font and size of the labels
        fresh: {
            fontFamily: "inconsolata",
            fontSize: 0.6,
            textAnchor: "middle",
            dominantBaseline: "central",
            stroke: "none",
            fill: "hsl(28deg, 70%, 55%)",
        },
        // the ring around the choice that has the focus
        focus: {
            ...factoryPaint.decoration,
        },
        // the look of the factory pinned to the class that has the focus, drawn as a ghost
        preview: {
            // the name the factory would have
            title: {
                fontFamily: "noto-italic",
                fontSize: 0.65,
                textAnchor: "middle",
                stroke: "none",
                fill: "hsl(28deg, 70%, 60%)",
                opacity: 0.8,
            },
            // the connectors to its slots
            connector: {
                fill: "none",
                stroke: "hsl(28deg, 70%, 55%)",
                strokeWidth: 1,
                strokeDasharray: "3 3",
                vectorEffect: "non-scaling-stroke",
                opacity: 0.7,
            },
            // the slots it would let go of
            dropped: {
                fill: "none",
                stroke: "hsl(0deg, 60%, 55%)",
                strokeWidth: 1,
                strokeDasharray: "3 3",
                vectorEffect: "non-scaling-stroke",
                opacity: 0.8,
            },
            // the terminals that would gain connectors
            plex: {
                fill: "none",
                stroke: "hsl(28deg, 70%, 55%)",
                strokeWidth: 1,
                vectorEffect: "non-scaling-stroke",
                opacity: 0.7,
            },
            // its slots
            slot: {
                fill: "none",
                stroke: "hsl(0deg, 0%, 70%)",
                strokeWidth: 1,
                strokeDasharray: "3 3",
                vectorEffect: "non-scaling-stroke",
            },
            // their names
            name: {
                fontFamily: "inconsolata",
                fontSize: 0.5,
                textAnchor: "middle",
                stroke: "none",
                fill: "hsl(0deg, 0%, 75%)",
            },
        },
        // the name of a satellite
        label: {
            fontFamily: "inconsolata",
            fontSize: 0.6,
            stroke: "none",
            fill: "hsl(0deg, 0%, 85%)",
        },
        // the way back: a small, quiet word, a little brighter under the pointer
        undo: {
            // at rest
            rest: {
                fontFamily: "rubik-light",
                fontSize: 0.38,
                textAnchor: "middle",
                stroke: "none",
                fill: "hsl(0deg, 0%, 50%)",
            },
            // under the pointer
            hover: {
                fontFamily: "rubik-light",
                fontSize: 0.38,
                textAnchor: "middle",
                stroke: "none",
                fill: "hsl(0deg, 0%, 80%)",
            },
        },
        // how much the rest of the diagram fades while the fan is out
        dim: 0.22,
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
