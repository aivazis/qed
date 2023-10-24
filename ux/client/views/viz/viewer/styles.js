// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// get colors
import { theme, wheel } from '~/palette'
// and the base styles
import styles from '../styles'


// the mixers
// the {viewer} shows some metadata with structure from {~/widgets/meta}
// the mixer
const viewer = {
    box: {
        ...styles.meta.box,
    },
    entry: {
        ...styles.meta.entry,
    },
    attribute: {
        ...styles.meta.attribute,
        width: "10.0em",
    },
    separator: {
        ...styles.meta.separator,
    },
    value: {
        ...styles.meta.value,
    },
}


// the viewer tab
const tab = state => ({
    // styling
    backgroundColor: state === "selected" ? "hsl(0deg, 0%, 12%)" : "hsl(0deg, 0%, 10%)",
    // for me
    flex: "0 0 auto",
    height: "1.6rem",
    // for my children
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
})


// for the {selector} in the {tab}
const selector = state => ({
    // the container
    box: {
        ...selectorPaint.base.box, ...selectorPaint[state].box
    },
    // the reader name
    name: {
        ...selectorPaint.base.name, ...selectorPaint[state].name
    },
    // the dataset selector
    selector: {
        ...selectorPaint.base.selector, ...selectorPaint[state].selector
    },
    // the separator
    separator: {
        ...selectorPaint.base.separator, ...selectorPaint[state].separator
    },
})
// its paint
const selectorPaint = {
    base: {
        box: {
            cursor: "default",
            vertcalAlign: "center",
            paddingBottom: "0.25rem",
        },
        name: {
            fontFamily: "rubik-light",
            fontSize: "80%",
        },
        selector: {
            fontFamily: "inconsolata",
            fontSize: "80%",
        },
        separator: {
            fontFamily: "inconsolata",
            fontSize: "80%",
            padding: "0.0rem 0.25rem",
        },
    },

    enabled: {
        box: {},
        name: {},
        selector: {},
        separator: {},
    },

    selected: {
        box: {},
        name: {
            color: theme.page.name,
        },
        selector: {
            color: theme.page.name,
        },
        separator: {
            color: wheel.gray.concrete,
        },
    },
}


// common paint for my badges, in normal form
const badge = {
    // the icon container
    badge: {
        base: {
            // for me
            flex: "0 0 auto",
            padding: "0.0rem 0.5rem",
            cursor: "pointer",
            // for my children
            display: "flex",
            alignItems: "center",
        },
        disabled: {},
        enabled: {},
        selected: {},
        available: {},
    },

    // for the shape container
    shape: {
        base: {},
        disabled: {},
        enabled: {
            // dim it a bit
            strokeOpacity: 0.5,
        },
        selected: {},
        available: {
            // full intensity
            strokeOpacity: 1.0,
        },
    },

    // for the icon main features
    icon: {
        base: {},
        disabled: {},
        enabled: {},
        selected: {},
        available: {},
    },

    // for the icon decoration
    decoration: {
        base: {},
        disabled: {},
        enabled: {},
        selected: {},
        available: {},
    },
}


// the button that dismisses a view
const collapse = {
    // inherit
    ...badge,
}


// the button that turns on the measuring layer
const measure = {
    // inherit
    ...badge,

    badge: {
        ...badge.badge,
        base: {
            ...badge.badge.base,
            // for me
            justifySelf: "end",
        },
    },

    icon: {
        ...badge.icon,
        selected: {
            ...badge.icon.selected,
            stroke: theme.page.name,
        },
        available: {
            ...badge.icon.available,
            stroke: theme.page.name,
        },
    },
}


// the button that splits a view
const split = {
    // inherit
    ...badge,

    badge: {
        ...badge.badge,
        base: {
            ...badge.badge.base,
            // for me
            justifySelf: "end",
        },
    },

    icon: {
        ...badge.icon,
        selected: {
            ...badge.icon.selected,
            stroke: theme.page.name,
        },
        available: {
            ...badge.icon.available,
            stroke: theme.page.name,
        },
    },
}


// the button that toggles the sync status of a data viewport
const sync = {
    // inherit
    ...badge,

    // the icon container
    badge: {
        ...badge.badge,
        base: {
            ...badge.badge.base,
            // for me
            justifySelf: "end",
        },
    },

    icon: {
        ...badge.icon,
        selected: {
            ...badge.icon.selected,
            stroke: theme.page.name,
        },
        available: {
            ...badge.icon.available,
            stroke: theme.page.name,
        },
    },

    decoration: {
        ...badge.decoration,

        selected: {
            ...badge.decoration.selected,
            fill: theme.page.name,
            stroke: theme.page.name,
        },
        available: {
            ...badge.decoration.available,
            stroke: theme.page.name,
        },
    }
}


// the button that prints the screen
const print = {
    // inherit
    ...badge,

    // the icon container
    badge: {
        ...badge.badge,
        base: {
            ...badge.badge.base,
            // for me
            justifySelf: "end",
        },
    },

    icon: {
        ...badge.icon,
        available: {
            ...badge.icon.available,
            stroke: theme.page.name,
        },
    },

    decoration: {
        ...badge.decoration,
        available: {
            ...badge.decoration.available,
            stroke: theme.page.name,
        },
    }
}


// the blank view
// structure from {~/widgets/badge}
const blank = {
    // the container
    placeholder: {
        flex: "1 1 auto",
        minWidth: "300px",
    },

    // the icon container
    icon: {
        // placement
        display: "block",
        width: "300px",
        height: "300px",
        position: "relative",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
    },

    // the graphics
    shape: {
        icon: {
            // stroke
            stroke: theme.page.name,
            strokeWidth: 3,
            // fill
            fill: "none",
        },
    },

    // for the user instructions
    message: {
        fontFamily: "inconsolata",
        fontSize: "120%",
        textAlign: "center",
    },
}


// publish
export default {
    blank,
    collapse,
    measure,
    print,
    selector,
    split,
    sync,
    tab,
    viewer,
}


// end of file
