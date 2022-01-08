// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// get the base styles
import base from '~/views/styles'


// the flex container
const flex = {
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
const activityPanels = {
    // the panel
    panel: {
        // inherit
        ...flex.panel,
        // make it stand out a bit
        backgroundColor: "hsl(0deg, 0%, 7%, 1)",
        // set up the preferred initial width
        width: "350px",
        flex: "0 0 auto",
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


// the panel with the known datasets
const datasets = {
    // inherit
    ...activityPanels,
}


// the panel with the rendering controls
const controls = {
    // inherit
    ...activityPanels,
}


// the blank view
const blank = {
    // the container
    nyi: {
        // inherit
        ...base.panel,
    },

    placeholder: {
        position: "relative",
        top: "50%",
        left: "50%",
        height: "400px",
        textAlign: "center",
        transform: "translate(-50%, -50%)",
    },

    icon: {
        // placement
        margin: "1.0em auto",
        width: "300px",
        height: "300px",
    },

    shape: {
        icon: {
            // stroke
            stroke: theme.page.name,
            strokeWidth: 3,
            // fill
            fill: "none",
        },
    },

    message: {
        fontFamily: "inconsolata",
        fontSize: "120%",
        textAlign: "center",
    },

}


// the tray with the data sources
const reader = {
    // for the tray
    tray: {
        box: {},
        header: {},
        title: {},
        items: {},
    },

    // for the tray that corresponds to the active view
    activeTray: {
        box: {},
        header: {},
        title: {
            color: theme.page.name,
        },
        items: {},
    },
}


// for the various dataset attributes
const attributes = {
    info: {
        fontSize: "60%",
        fontFamily: "rubik-light",
    },
    name: {
        display: "inline-block",
        width: "7em",
        textAlign: "right",
    },
    value: {},
    separator: {
        width: "1.5em",
    }
}


// dataset selectors
const selectors = {
    info: {
        fontSize: "60%",
        fontFamily: "rubik-light",
        backgroundColor: "hsl(0deg, 0%, 10%)",
    },
    name: {
        display: "inline-block",
        width: "7em",
        textAlign: "right",
    },
    value: {},
    separator: {
        width: "1.5em",
    }
}


// dataset channels
const channel = {
    box: {
        fontSize: "60%",
        fontFamily: "inconsolata",
        display: "flex",
        flexDirection: "row",
    },

    name: {
        base: {
            flex: 1,
            padding: "0.125em 0.0em 0.125em 9.5em",
            cursor: "pointer",
        },
        enabled: {
            color: wheel.gray.aluminum,
        },
        available: {
            color: theme.page.name,
        },
        active: {
            color: theme.page.name,
        },
    },
}


// the viewer tab
const tab = {
    // the container
    box: {
        // for me
        flex: "0 0 auto",
        height: "1.6rem",
        // styling
        backgroundColor: "hsl(0deg, 0%, 10%, 1)",
        // for my children
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
    },

    active: {
        color: wheel.gray.concrete,
    },

    // the name of the dataset
    dataset: {
        fontFamily: "rubik-light",
        fontSize: "80%",
        textTransform: "uppercase",
        paddingTop: "0.1rem",
    },

    // styling for selector and channel names
    selector: {
        fontFamily: "inconsolata",
        fontSize: "80%",
    },

    // separator for the selector and channel names
    separator: {
        fontFamily: "inconsolata",
        fontSize: "80%",
        padding: "0.0rem 0.25rem",
    },
}


// the button that dismisses a view
const collapse = {
    // the icon container
    badge: {
        // for me
        flex: "0 0 auto",
        padding: "0.0rem 0.5rem",
        cursor: "pointer",
        // for my children
        display: "flex",
        alignItems: "center",
    },
    // for the shape container
    shape: {
        // dim it a bit
        strokeOpacity: 0.5,
    },

    // for the shape
    icon: {
        strokeWidth: 2,
    },

    // highlight when the cursor hovers over it
    available: {
        shape: {
            // full intensity
            strokeOpacity: 1.0,
        },
    },
}


// the button that splits a view
const split = {
    // the icon container
    badge: {
        // for me
        flex: "0 0 auto",
        justifySelf: "end",
        padding: "0.0rem 0.5rem",
        cursor: "pointer",
        // for my children
        display: "flex",
        alignItems: "center",
    },

    // for the shape container
    shape: {
        // dim it a bit
        strokeOpacity: 0.5,
    },

    // for the shape
    icon: {
        stroke: wheel.gray.flour,
    },

    // highlight when the cursor hovers over it
    available: {
        shape: {
            // full intensity
            strokeOpacity: 1.0,
        },
    },
}


// the button that toggles the sync status of a data viewport
const sync = {
    // the icon container
    badge: {
        // for me
        flex: "0 0 auto",
        justifySelf: "end",
        padding: "0.0rem 0.5rem",
        cursor: "pointer",
        // for my children
        display: "flex",
        alignItems: "center",
    },

    // for the shape container
    shape: {
        // dim it a bit
        strokeOpacity: 0.5,
    },

    // for the shape
    icon: {
        stroke: wheel.gray.flour,
    },

    // highlight when the cursor hovers over it
    available: {
        shape: {
            // full intensity
            strokeOpacity: 1.0,
        },
    },
}


// the dataset mosaic styling
const mosaic = {
    // the overall box
    box: {
        // layout
        flex: "1 1 100%",
        overflow: "auto",
        // minWidth: "300px",
        // minHeight: "300px",
        margin: "0.25rem 0.5rem 0.5rem 0.5rem",
        border: "1px solid hsl(28deg, 30%, 15%)",
    },

    // the tile container
    mosaic: {
        minWidth: "300px",
        minHeight: "300px",
        backgroundColor: "hsl(0deg, 5%, 7%)",
    },

    // individual tiles
    tile: {
        backgroundColor: "hsl(240deg, 25%, 7%)",
    },
}


// publish
export default {
    attributes,
    blank,
    channel,
    collapse,
    controls,
    datasets,
    flex,
    mosaic,
    reader,
    selectors,
    split,
    sync,
    tab,
}


// end of file
