// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from "react"

//local
// hooks
import { useFetchArchives } from "./useFetchArchives"

// the provider factory
export const Provider = ({ children }) => {
    // ask the server for all known data archives
    const piles = useFetchArchives()
    // attach them as read-only state
    const [archives] = React.useState(piles)

    // build the initial context value
    const context = {
        // the data archives
        archives,
    }

    // provide for my children
    return (
        <Context.Provider value={context}>
            {children}
        </Context.Provider>
    )
}

// the context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provide
    {
        // the data archives
        archives: [],
    }
)

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'archives' context: no provider"


// end of file
