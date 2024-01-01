// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from "react"

// local
// context
import { Context } from "./context"


// access to the archive in {context}
export const useArchive = () => {
    // grab the archive
    const { archive } = React.useContext(Context)
    // and share it
    return archive
}


// end of file
