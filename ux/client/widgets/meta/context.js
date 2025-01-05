// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'


// the provider factory
export const Provider = ({ min, initial, max, children }) => {
    // record the range of detail
    const [range] = React.useState([min, max])
    // and the current level
    const [detail, setDetail] = React.useState(initial)

    // build the initial context value
    const context = {
        // the range
        range,
        // access to the current value
        detail, setDetail,
    }

    // provide for my children
    return (
        <Context.Provider value={context}>
            {children}
        </Context.Provider>
    )
}


// set up the application context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provider
    {
        // record the range of detail
        range: null,
        // and the current level
        detail: null,
        setDetail: () => { throw new Error(complaint) },
    }
)


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'meta' context: no provider"


// end of file
