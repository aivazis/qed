// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from "react"
import { graphql, useFragment } from 'react-relay/hooks'


// the provider factory
export const Provider = ({ qed, children }) => {
    // ask it for all known data archives and attach them as read-only state
    const { archives } = useFragment(graphql`
        fragment context_archives on QED {
            archives {
                id
                name
                uri
                readers
            }
        }`,
        qed
    )
    // the set of known views; it starts out with one empty vew
    const [views, setViews] = React.useState([emptyView()])
    //  the active viewport is an index into the set of views
    const [activeViewport, setActiveViewport] = React.useState(0)

    // build the initial context value
    const context = {
        // the data archives
        archives,

        // the known views
        views, setViews,
        // the active viewport
        activeViewport, setActiveViewport,
        // the default view factory
        emptyView,
    }

    // provide for my children
    return (
        <Context.Provider value={context}>
            {children}
        </Context.Provider>
    )
}

// the context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provide
    {
        // the data archives
        archives: [],

        // the known views
        views: null,
        setViews: () => { throw new Error(complaint) },
        // the active viewport
        activeViewport: null,
        setActiveViewport: () => { throw new Error(complaint) },
        // the default view factory
        emptyView,
    }
)

// the empty view template
export const emptyView = () => ({
    archive: null, reader: null,
})
// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'archives' context: no provider"


// end of file
