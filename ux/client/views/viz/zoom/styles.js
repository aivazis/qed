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
            ...zoomPaint.base.meta.entry,
            ...zoomPaint[state].meta.entryibute
        },
        separator: {
            ...styles.meta.separator,
            ...zoomPaint.base.meta.entry,
            ...zoomPaint[state].meta.entryrator
        },
        value: {
            ...styles.meta.value,
            ...zoomPaint.base.meta.entry,
            ...zoomPaint[state].meta.entry
        },
    }
})


// styling for the controller
// colors for the parts
const ink = "hsl(0deg, 0%, 60%)"
const paint = "hsl(0deg, 0%, 20%)"
const detail = "hsl(0deg, 0%, 50%)"

const highlight = theme.page.name


const controller = {
    box: {
        margin: "1.0rem auto",
        border: "1px solid hsl(0deg, 0%, 15%)",
    },

    axis: {
        fill: "none",
        stroke: ink,
        strokeWidth: 7,
    },

    tick: {
        fill: "none",
        stroke: detail,
        strokeWidth: 5,
    },
}


// styling for the indicator
const indicator = ({ state, polish }) => ({
    ...indicatorPaint.base,
    ...indicatorPaint[state],
    ...(polish ? indicatorPaint["available"] : null)
})


// styling for the label
const label = ({ state, polish }) => ({
    ...labelPaint.base,
    ...labelPaint[state],
    ...(polish ? labelPaint["available"] : null)
})


// publish
export default {
    controller,
    indicator,
    label,
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


// for the indicator
const indicatorPaint = {
    base: {
        cursor: "pointer",
        strokeWidth: 3,
    },

    disabled: {
        cursor: "default",
        fill: paint,
        stroke: paint,
    },

    enabled: {
        fill: paint,
        stroke: ink,
    },

    selected: {
        fill: highlight,
        stroke: highlight,
    },

    available: {
        fill: highlight,
        stroke: highlight,
    },
}


// for the indicator
const labelPaint = {
    base: {
        fontFamily: "inconsolata",
        fontSize: "75px",
        textAnchor: "middle",
        stroke: "none",
    },

    disabled: {
        cursor: "default",
        fill: paint,
    },

    enabled: {
        cursor: "pointer",
        fill: ink,
    },

    selected: {
        cursor: "default",
        fill: highlight,
    },

    available: {
        fill: highlight,
    },
}


// end of file
