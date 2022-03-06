// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'


// the provider factory
export const Provider = ({ children }) => {

    // set up the context
    const context = {
    }

    // provide for my children
    return (
        <Context.Provider value={context}>
            {children}
        </Context.Provider>
    )
}


// set up the viewer context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provider
    {
    }
)


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viewer' context: no provider"


// end of file
