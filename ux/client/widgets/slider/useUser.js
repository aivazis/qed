// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from "react"


// local
// context
import { Context } from "./context"


// provide access to the converter from mouse coordinates to use values
export const useUser = () => {
    // pull what i need from {context}
    const {
        mouseToUser, mouseDeltaToUser,
    } = React.useContext(Context)

    // and publish it
    return { mouseToUser, mouseDeltaToUser }
}


// end of file
