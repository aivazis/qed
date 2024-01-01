// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// base styling for all uses of {meta} here
// entity meta data: structure from {~/widgets/meta}
// the base layer
const meta = {
    // the overall table: three columns: {attribute}, {separator}, {value}
    box: {
        fontFamily: "rubik-light",
        color: theme.header.color,
    },
    // for each row
    entry: {},
    // the name of the attribute
    attribute: {},
    // the separator
    separator: {},
    // the value of the attribute
    value: {
        fontFamily: "inconsolata",
        color: wheel.gray.aluminum,
    },
}


// common paint for controls, in normal form
const control = {
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



// publish
export default {
    meta,
    control,
}


// end of file
