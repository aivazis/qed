// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from "react"


// local
// context
import { Context } from "./context"


// provide access to the {sliding} flag
export const useClient = () => {
    // pull what i need from {context}
    const {
        emplace,
    } = React.useContext(Context)

    // and publish it
    return { emplace }
}


// end of file
