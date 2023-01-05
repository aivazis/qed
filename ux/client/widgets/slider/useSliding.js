// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from "react"


// local
// context
import { Context } from "./context"


// provide access to the {sliding} indicator id
export const useSliding = () => {
    // grab the sliding indicator
    const { cursor, sliding } = React.useContext(Context)
    // and return it
    return { cursor, sliding }
}


// end of file
