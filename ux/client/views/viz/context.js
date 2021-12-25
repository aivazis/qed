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
        // the active view
        activeView: null,
        setActiveView: () => { throw new Error(complaint) },
        // update the contents of the active view
        viewChannel: () => { throw new Error(complaint) },
    }
)


// the provider factory
export const Provider = ({
    // children
    children
}) => {
    // setup the views
    const [views, setViews] = React.useState(new Array())
    // the active is an index into the {views}
    const [activeView, setActiveView] = React.useState(0)

    // split a view
    const splitView = (view) => { }
    // collapse a view
    const collapseView = (view) => { }

    // update the contents of the active view
    const viewChannel = (channel) => {
        // adjust the view
        setViews((old) => {
            // make a copy of the old state
            const clone = [...old]
            // adjust the entry that corresponds to the active view
            clone[activeView] = channel
            // and hand off the new state
            return clone
        })
        // all done
        return
    }

    // build the current value of the context
    const context = {
        // the views
        views, collapseView, splitView,
        // active view
        activeView, setActiveView,
        // modify the contents of the active view
        viewChannel,
    }

    // provide for my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider >

    )
}


// end of file
