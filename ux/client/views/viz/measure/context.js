// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from 'react'


// the provider factory
export const Provider = ({ children }) => {
    // the set of selected nodes
    const [selection, setSelection] = React.useState(new Set())

    // build the initial context value
    const context = {
        // selected nodes
        selection, setSelection,
    }

    // provide from my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider>
    )
}


// set up the {marker} context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provider
    {
        // selected nodes
        selection: null,
        setSelection: () => { throw new Error(complaint) },
    }
)


// the error message that consumers see when accessing the context outside a provider
const complaint = "while accessing the 'slider' context: no provider"


// end of file
