// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useFetchQED } from './useFetchQED'

// the provider factory
export const Provider = ({ children }) => {
    // get the session
    const qed = useFetchQED()

    // build the current value of the context
    const context = {
        // the session
        qed,
    }
    // provide for my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider >

    )
}

// setup the flex context
export const Context = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // the session
        qed: null,
    }
)


// end of file
