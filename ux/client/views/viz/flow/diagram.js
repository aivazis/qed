// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'


// the diagram on the canvas: its id, which the requests that change it name, and whether every
// step of a drag goes to the server
const Context = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // no diagram
        id: null,
        // so nothing to send steps to
        live: false,
    }
)


// the provider
export const DiagramProvider = ({ id, live, children }) => {
    // provide for my children
    return (
        <Context.Provider value={{ id, live }}>
            {children}
        </Context.Provider>
    )
}


// access to the diagram on the canvas
export const useDiagram = () => {
    // pull it from the context
    return React.useContext(Context)
}


// end of file
