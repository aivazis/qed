// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// get colors
import { theme, wheel } from "~/palette"
// paint for my badges
import { control, selector as baseSelector } from '../explorer/styles'


// just use the base selector
export const selector = baseSelector


// the button that connects a new archive
export const connect = {
    // inherit
    ...control,
}


// end of file