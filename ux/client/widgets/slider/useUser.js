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
export const useUser = () => {
    // pull what i need from {context}
    const {
        mouseToUser,
    } = React.useContext(Context)

    // and publish it
    return { mouseToUser }
}


// end of file
