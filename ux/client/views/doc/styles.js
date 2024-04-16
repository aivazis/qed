// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// base styling for all uses of {meta} here
// entity meta data: structure from {~/widgets/meta}
// the base layer
export const meta = {
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


// end of file
