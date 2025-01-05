// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from "react"


// the provider factory
export const Provider = ({ archive, children }) => {
    // build the initial context value
    const context = {
        // the data archive
        archive,
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
    // the default value clients see when accessing the context outside a provider
    {
        // the data archive
        archive: null,
    }
)

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'archive' context: no provider"


// end of file
