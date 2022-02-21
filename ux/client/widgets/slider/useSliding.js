// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"


// local
// context
import { Context } from "./context"


// provide access to the {sliding} flag
export const useSliding = () => {
    // grab the sliding indicator
    const { sliding } = React.useContext(Context)
    // and return it
    return sliding
}


// end of file
