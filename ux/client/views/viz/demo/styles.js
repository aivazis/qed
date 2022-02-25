// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// and my base styles
import styles from '../styles'


// the mixers
const demo = state => ({
    // for the tray
    tray: {
        box: { ...demoPaint.base.tray.box, ...demoPaint[state].tray.box },
        header: { ...demoPaint.base.tray.header, ...demoPaint[state].tray.header },
        title: { ...demoPaint.base.tray.title, ...demoPaint[state].tray.title },
        items: { ...demoPaint.base.tray.items, ...demoPaint[state].tray.items },
    },
})


// publish
export default {
    demo,
}


// the paint
// for {demo}
const demoPaint = {
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
