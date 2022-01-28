// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// and my base styles
import styles from '../styles'


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
            ...styles.meta.box,
            ...readerPaint.base.meta.box,
            ...readerPaint[state].meta.box
        },
        entry: {
            ...styles.meta.entry,
            ...readerPaint.base.meta.entry,
            ...readerPaint[state].meta.entry
        },
        attribute: {
            ...styles.meta.attribute,
            ...readerPaint.base.meta.entry,
            ...readerPaint[state].meta.entryibute
        },
        separator: {
            ...styles.meta.separator,
            ...readerPaint.base.meta.entry,
            ...readerPaint[state].meta.entryrator
        },
        value: {
            ...styles.meta.value,
            ...readerPaint.base.meta.entry,
            ...readerPaint[state].meta.entry
        },
    }
})

// {axis} entries: structure from {~/widgets/meta}
const axis = () => ({
    box: { ...styles.meta.box, ...axisPaint.box },
    entry: { ...styles.meta.entry, ...axisPaint.entry },
    attribute: { ...styles.meta.attribute, ...axisPaint.attribute },
    separator: { ...styles.meta.separator, ...axisPaint.separator },
    value: { ...styles.meta.value, ...axisPaint.info },
})

// {coordinate} entries; {state} x structure from {~/widgets/meta}
// valid {coordinate} states: {disabled}, {enabled}, {available}, {selected}
const coordinate = (state, polish) => ({
    ...coordinatePaint.base,
    ...coordinatePaint[state],
    ...(polish ? coordinatePaint.available : null),
})

// {channels} entries: structure from {~/widgets/meta}
const channels = () => ({
    box: { ...styles.meta.box, ...channelsPaint.box },
    entry: { ...styles.meta.entry, ...channelsPaint.entry },
    attribute: { ...styles.meta.attribute, ...channelsPaint.attribute },
    separator: { ...styles.meta.separator, ...channelsPaint.separator },
    value: { ...styles.meta.value, ...channelsPaint.info },
})

// {channel} entries; {state} x structure from {~/widgets/meta}
// valid {channel} states: {enabled}, {available}, {selected}
const channel = (state, polish) => ({
    ...channelPaint.base,
    ...channelPaint[state],
    ...(polish ? channelPaint.available : null),
})


const mark = {
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
    mark,
    reader,
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
        display: "inline-block",
        cursor: "pointer",
        margin: "0.0em 1.0em 0.0em 0.0em",
    },

    disabled: {
        cursor: "default",
        color: wheel.gray.gabro,
        // N.B.:
        //   dimming disabled coordinates using opacity seems to trigger a table rendering bug
        //   in safari where expanding/collapsing surrounding reader trays would leave the disabled
        //   value at the same spot on the screen, even though the DOM is correct; to reproduce,
        //   uncomment the line below and rebuild
        //   last checked: safari Version 15.2 (15612.3.6.1.8, 15612)
        // opacity: "0.25",
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
        display: "inline-block",
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


// end of file
