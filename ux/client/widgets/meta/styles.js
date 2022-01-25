// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// paint
const box = {}

const entry = {
    cursor: "default",
    lineHeight: "150%",
    verticalAlign: "baseline",
}

const attribute = {
    textTransform: "uppercase",
    textAlign: "right",
    padding: "0.0em 0.0em 0.0em 0.5em",
    width: "30%",
}

const separator = {
    width: "1.0em",
    padding: "0.0em 0.25em 0.0em 0.25em",
    textAlign: "center",
}

const value = {
    // layout
    padding: "0.0em 0.5em 0.0em 0.0em",
    // for my children
    textAlign: "left",
    textOverflow: "ellipsis",
    display: "flex",
    flexDirection: "row",
    flexWrap: "wrap",
}

const detail = {
    box: {
        fontSize: "75%",
        fontWeight: "normal",
        textAlign: "right",
        textTransform: "lowercase",
        padding: "0.25em 0.0em",
        cursor: "default",
    },

    control: {
        // basic style
        base: {
            fontFamily: "rubik-light",
            textTransform: "uppercase",
            display: "inline-block",
            margin: "0.0em 0.5em",
            color: wheel.gray.aluminum,
        },
        // when disabled
        disabled: {
            opacity: 0.25,
        },
        // when enabled
        enabled: {
            cursor: "pointer",
        },
        // when highlighted
        available: {
            color: theme.page.name,
        },
    },
}


// mixers
const detailControl = (state, polish) => ({
    ...detail.control.base,
    ...detail.control[state],
    ...(polish ? detail.control.available : {})
})


// publish
export default {
    attribute,
    box,
    detail,
    detailControl,
    entry,
    separator,
    value,
}

// end of file
