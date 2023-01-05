// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from "react"


// local
// context
import { Context } from "./context"


// provide access to the {sliding} flag
export const useMine = () => {
    // pull what i need from {context}
    const {
        bboxMine, mainMine, crossMine,
    } = React.useContext(Context)

    // and publish it
    return { bboxMine, mainMine, crossMine, }
}


// end of file
