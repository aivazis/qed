// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from "react"
import { graphql, useFragment } from 'react-relay/hooks'

// the provider factory
export const Provider = (props) => {
    // extract the data
    const archive = useFragment(graphql`
        fragment context_archive on Archive {
            id
            name
            uri
        }`,
        props.archive
    )

    // build the initial context value
    const context = {
        // the data archive
        archive,
    }

    // provide for my children
    return (
        <Context.Provider value={context}>
            {props.children}
        </Context.Provider>
    )
}

// the context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provide
    {
        // the data archives
        archive: [],
    }
)

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'archive' context: no provider"


// end of file
