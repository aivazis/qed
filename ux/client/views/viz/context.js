// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viz' context: no provider"

// setup the flex context
export const Context = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // the views
        views: [],
        splitView: () => { throw new Error(complaint) },
        collapseView: () => { throw new Error(complaint) },

    }
)


// the provider factory
export const Provider = ({
    // children
    children
}) => {
    // setup the views
    const [views, setViews] = React.useState(new Array())
    // split a view
    const splitView = (view) => { }
    const collapseView = (view) => { }

    // build the current value of the context
    const context = {
        // the views
        views, collapseView, splitView,
    }

    // provide for my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider >

    )
}


// end of file
