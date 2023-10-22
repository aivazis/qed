// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// get colors
import { theme, wheel } from "~/palette"


// the flex container
export const flex = {
    // the overall flex container
    box: {
        flex: "1 1 100%",
        minWidth: "800px", // DO NOT REMOVE THIS; IT FORCES flex TO LOOK AT THE WIDTH OF THE PANEL
        backgroundColor: "hsl(0deg, 0%, 10%)",
    },

    // individual panels
    panel: {
        // styling
        backgroundColor: "hsl(0deg, 0%, 5%, 1)",
        // for my children
        display: "flex",
        flexDirection: "column",
    },

    // the inter-panel separator
    separator: {
        // the line
        rule: {
            backgroundColor: "hsl(0deg, 0%, 15%, 0.5)",
        },
        // the handle
        handle: {},
    },
}

// the activity panels
export const activityPanels = {
    // the panel
    panel: {
        // inherit
        ...flex.panel,
        // make it stand out a bit
        backgroundColor: "hsl(0deg, 0%, 7%, 1)",
        // shut flex down for this panel
        flex: "0 0 auto",
        // and set up the preferred initial width
        width: "400px",
        // show scroll bars when we run out of room
        overflow: "auto",
    },

    // the separator
    separator: {
        // inherit
        ...flex.separator,
    },

    header: {
        // make it stand out a bit
        backgroundColor: "hsl(0deg, 0%, 7%, 1)",
    },
}

// the viewer tab
export const tab = state => ({
    // styling
    fontSize: "75%",
    backgroundColor: state === "selected" ? "hsl(0deg, 0%, 12%)" : "hsl(0deg, 0%, 10%)",
    // for me
    flex: "0 0 auto",
    height: "1.6rem",
    // for my children
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
})


// the blank view
export const blank = {
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


// common paint for my badges, in normal form
export const badge = {
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
export const collapse = {
    // inherit
    ...badge,
}


// normal controls
export const control = {
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
export const split = {
    // inherit
    ...control,
}

// for the {selector} in the {tab}
export const selector = state => ({
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
            overflow: "hidden",
            whiteSpace: "nowrap",
            textOverflow: "ellipsis",
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


// end of file
