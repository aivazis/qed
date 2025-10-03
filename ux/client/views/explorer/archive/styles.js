// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// get colors
import { theme, wheel } from "~/palette"
// paint for my badges
import { badge, control, selector as baseSelector } from '../explorer/styles'


// just use the base selector
export const selector = baseSelector


// the button that connects a new archive
export const connect = {
    // inherit
    ...control,
}

// the button that adds a vertex to a pile
export const add = {
    // inherit
    ...badge,
}

// the button that deletes a vertex from a pile
export const del = {
    // inherit
    ...badge,
}


// end of file
