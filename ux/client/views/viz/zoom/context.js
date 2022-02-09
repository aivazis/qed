// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"


// the provider factory
export const Provider = ({ children }) => {
    // make a flag that indicates whether the zoom level is being adjusted by dragging the
    // control
    const [zooming, setZooming] = React.useState(false)

    // build the initial context value
    const context = {
        // the flag and its mutator
        zooming, setZooming
    }

    // provide from my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider>
    )
}


// set up the {zoom} context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provider
    {
        // the zooming indicator
        zooming: null,
        setZooming: () => { throw new Error(complaint) },
    }
)


// the error message that consumers see when accessing the context outside a provider
const complaint = "while accessing the 'zoom' context: no provider"


// end of file
