// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { theme } from '~/palette'
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
        width: "10em",
    },
    separator: {
        ...styles.meta.separator,
    },
    value: {
        ...styles.meta.value,
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
    viewer,
}


// end of file
