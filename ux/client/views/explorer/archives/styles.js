// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// get colors
import { wheel, theme } from '~/palette'

// the base styling for children of the {explorer} panel
import { activityPanels as panelPaint, collapse } from '../explorer/styles'
// paint for the metadata container
import { meta as metaPaint } from '../styles'

// my header
export const header = {
    // inherit
    ...panelPaint.header
}


// the paint mixers
// repositories
export const archive = state => ({
    // for the metadata
    meta: {
        box: {
            ...metaPaint.box,
            ...archivePaint.base.meta.box,
            ...archivePaint[state].meta.box,
        },
        entry: {
            ...metaPaint.entry,
            ...archivePaint.base.meta.entry,
            ...archivePaint[state].meta.entry,
        },
        attribute: {
            ...metaPaint.attribute,
            ...archivePaint.base.meta.attribute,
            ...archivePaint[state].meta.attribute,
        },
        separator: {
            ...metaPaint.separator,
            ...archivePaint.base.meta.separator,
            ...archivePaint[state].meta.separator,
        },
        value: {
            ...metaPaint.value,
            ...archivePaint.base.meta.value,
            ...archivePaint[state].meta.value,
        },
    }
})

// directories
export const directory = state => {
    // assemble and return
    return {
        ...directoryPaint.base,
        ...directoryPaint[state],
    }
}

// files
export const file = state => {
    // assemble and return
    return {
        ...filePaint.base,
        ...filePaint[state],
    }
}

// the button that disconnects an archive
export const disconnect = {
    // inherit
    ...collapse,
}


// the paint
// for the {archive} mixer
const archivePaint = {
    // base state
    base: {
        meta: {
            box: {},
            entry: {},
            attribute: {
                width: "2.0em",
                opacity: 0.5,
            },
            separator: {},
            value: {
                opacity: 0.5,
            },
        },
    },

    // when enabled
    enabled: {
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
        meta: {
            box: {},
            entry: {},
            attribute: {},
            separator: {},
            value: {},
        },
    },
}

const directoryPaint = {
    // base state
    base: {
    },

    // when enabled
    enabled: {
    },

    // when selected
    selected: {
        color: theme.page.name,
    },
}

const filePaint = {
    // base state
    base: {
        paddingTop: '0.25em',
        paddingRight: '1.0em',
        paddingBottom: '0.25em',
        paddingLeft: '1.0em',
        overflow: 'hidden',
        whiteSpace: 'nowrap',
        textOverflow: 'ellipsis',
        cursor: 'pointer',
    },

    // when enabled
    enabled: {
    },

    // when selected
    selected: {
        color: theme.page.name,
    },
}

// end of file
