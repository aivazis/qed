// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useFetchServerVersion } from './useFetchServerVersion'


// the provider factory
export const Provider = ({ children }) => {
    // ask the server its version
    const info = useFetchServerVersion()
    // attach them as read-only state
    const [serverVersion] = React.useState(info)

    // build the initial context value
    const context = {
        // the server version
        serverVersion,
    }

    // provide for my children
    return (
        <Context.Provider value={context}>
            {children}
        </Context.Provider>
    )
}


// set up the viz context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provider
    {
        // the server version
        serverVersion: null,
    }
)


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'qed' context: no provider"


// end of file
