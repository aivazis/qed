// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"


// local
// context
import { Context } from "./context"


// provide access to the {picking} flag
export const useStartPicking = () => {
    // grab the picking indicator
    const { picking } = React.useContext(Context)
    // and return it
    return picking
}


// end of file
