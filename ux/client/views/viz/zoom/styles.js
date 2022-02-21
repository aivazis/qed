// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// and my base styles
import styles from '../styles'


// the mixers
const zoom = state => ({
    // for the tray
    tray: {
        box: { ...zoomPaint.base.tray.box, ...zoomPaint[state].tray.box },
        header: { ...zoomPaint.base.tray.header, ...zoomPaint[state].tray.header },
        title: { ...zoomPaint.base.tray.title, ...zoomPaint[state].tray.title },
        items: { ...zoomPaint.base.tray.items, ...zoomPaint[state].tray.items },
    },
    // for the metadata
    meta: {
        box: {
            ...styles.meta.box,
            ...zoomPaint.base.meta.box,
            ...zoomPaint[state].meta.box
        },
        entry: {
            ...styles.meta.entry,
            ...zoomPaint.base.meta.entry,
            ...zoomPaint[state].meta.entry
        },
        attribute: {
            ...styles.meta.attribute,
            ...zoomPaint.base.meta.attribute,
            ...zoomPaint[state].meta.attribute,
        },
        separator: {
            ...styles.meta.separator,
            ...zoomPaint.base.meta.sparator,
            ...zoomPaint[state].meta.sparator,
        },
        value: {
            ...styles.meta.value,
            ...zoomPaint.base.meta.value,
            ...zoomPaint[state].meta.value,
        },
    }
})


// publish
export default {
    zoom,
}


// the paint
// for {zoom}
const zoomPaint = {
    // base state
    base: {
        tray: {
            box: {},
            header: {
                backgroundColor: "hsl(0deg, 0%, 12%)",
            },
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

    disabled: {
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
            header: {
                backgroundColor: "hsl(0deg, 0%, 17%)",
            },
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


// end of file
