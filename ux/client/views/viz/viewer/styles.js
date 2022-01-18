// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


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
        width: "7.0em",
    },
    separator: {
        ...styles.meta.separator,
    },
    value: {
        ...styles.meta.value,
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


// the blank view
// structure from {~/widgets/badge}
const blank = {
    // the container
    placeholder: {
        position: "relative",
        top: "50%",
        left: "50%",
        textAlign: "center",
        transform: "translate(-50%, -50%)",
    },

    // the icon container
    icon: {
        // placement
        width: "300px",
        height: "300px",
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
    tab,
    viewer,
}


// end of file
