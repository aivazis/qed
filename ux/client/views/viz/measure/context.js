// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from 'react'


// the provider factory
export const Provider = ({ children }) => {
    // a flag that indicates that the user has started dragging a {mark}
    const [moving, setMoving] = React.useState(null)

    // build the initial context value
    const context = {
        // movement indicator
        moving, setMoving,
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
        // movement
        moving: null,
        setMoving: () => { throw new Error(complaint) },
    }
)


// the error message that consumers see when accessing the context outside a provider
const complaint = "while accessing the 'measure' context: no provider"


// end of file
