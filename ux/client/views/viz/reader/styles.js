// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// the mixers
// the tray with the data sources
// structure from {~/widgets/tray} and {~/widgets/meta}
// valid {reader} states: {enabled}, {selected}
// the mixer
const reader = state => ({
    // for the tray
    tray: {
        box: { ...readerPaint.base.tray.box, ...readerPaint[state].tray.box },
        header: { ...readerPaint.base.tray.header, ...readerPaint[state].tray.header },
        title: { ...readerPaint.base.tray.title, ...readerPaint[state].tray.title },
        items: { ...readerPaint.base.tray.items, ...readerPaint[state].tray.items },
    },
    // for the metadata
    meta: {
        box: {
            ...metaPaint.box,
            ...readerPaint.base.meta.box,
            ...readerPaint[state].meta.box
        },
        entry: {
            ...metaPaint.entry,
            ...readerPaint.base.meta.entry,
            ...readerPaint[state].meta.entry
        },
        attribute: {
            ...metaPaint.attribute,
            ...readerPaint.base.meta.entry,
            ...readerPaint[state].meta.entryibute
        },
        separator: {
            ...metaPaint.separator,
            ...readerPaint.base.meta.entry,
            ...readerPaint[state].meta.entryrator
        },
        value: {
            ...metaPaint.value,
            ...readerPaint.base.meta.entry,
            ...readerPaint[state].meta.entry
        },
    }
})

// {axis} entries: structure from {~/widgets/meta}
const axis = () => ({
    box: { ...metaPaint.box, ...axisPaint.box },
    entry: { ...metaPaint.entry, ...axisPaint.entry },
    attribute: { ...metaPaint.attribute, ...axisPaint.attribute },
    separator: { ...metaPaint.separator, ...axisPaint.separator },
    value: { ...metaPaint.value, ...axisPaint.info },
})

// {coordinate} entries; {state} x structure from {~/widgets/meta}
// valid {coordinate} states: {disabled}, {enabled}, {available}, {selected}
const coordinate = state => ({
    ...coordinatePaint.base,
    ...coordinatePaint[state]
})

// {channels} entries: structure from {~/widgets/meta}
const channels = () => ({
    box: { ...metaPaint.box, ...channelsPaint.box },
    entry: { ...metaPaint.entry, ...channelsPaint.entry },
    attribute: { ...metaPaint.attribute, ...channelsPaint.attribute },
    separator: { ...metaPaint.separator, ...channelsPaint.separator },
    value: { ...metaPaint.value, ...channelsPaint.info },
})

// {channel} entries; {state} x structure from {~/widgets/meta}
// valid {channel} states: {enabled}, {available}, {selected}
const channel = state => ({
    ...channelPaint.base,
    ...channelPaint[state]
})


const required = {
    fontFamily: "inconsolata",
    color: "hsl(0deg, 100%, 50%)",
    padding: "0.0em 0.25em 0.0em 0.0em",
    verticalAlign: "baseline",
}

// publish
export default {
    axis,
    channel,
    channels,
    coordinate,
    reader,
    required,
}


// the paint
// for {reader}
const readerPaint = {
    // base state
    base: {
        tray: {
            box: {},
            header: {},
            title: {},
            items: {},
        },
        meta: {
            box: {},
            entry: {},
            attribute: {},
            separator: {},
            value: {},
        },
    },

    // when enabled
    enabled: {
        tray: {
            box: {},
            header: {},
            title: {},
            items: {},
        },
        meta: {
            box: {},
            entry: {},
            attribute: {},
            separator: {},
            value: {},
        },
    },

    // when selected
    selected: {
        tray: {
            box: {},
            header: {},
            title: {
                color: theme.page.name,
            },
            items: {},
        },
        meta: {
            box: {},
            entry: {},
            attribute: {},
            separator: {},
            value: {},
        },
    },
}


// for {axis}
const axisPaint = {
    box: {},
    entry: {},
    attribute: {},
    separator: {},
    value: {},
}

// for {coordinate}
const coordinatePaint = {
    base: {
        cursor: "pointer",
        margin: "0.0em 1.0em 0.0em 0.0em",
    },

    disabled: {
        cursor: "default",
        opacity: 0.25,
    },

    enabled: {},

    available: {
        color: theme.page.name,
    },

    selected: {
        color: theme.page.name,
    },
}

// for {channels}
const channelsPaint = {
    box: {},
    entry: {},
    attribute: {},
    separator: {},
    value: {},
}

// for {channel}
const channelPaint = {
    base: {
        cursor: "pointer",
        margin: "0.0em 1.0em 0.0em 0.0em",
    },

    enabled: {},

    available: {
        color: theme.page.name,
    },

    selected: {
        color: theme.page.name,
    },
}

// base styling for all uses of {meta} here
// entity meta data: structure from {~/widgets/meta}
// the base layer
const metaPaint = {
    // the overall table: three columns: {attribute}, {separator}, {value}
    box: {
        fontFamily: "rubik-light",
        fontSize: "60%",
        color: theme.header.color,
    },
    // for each row
    entry: {},
    // the name of the attribute
    attribute: {},
    // the separator
    separator: {},
    // the value of the attribute
    value: {
        fontFamily: "inconsolata",
        color: wheel.gray.aluminum,
    },
}


// end of file
