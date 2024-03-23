// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// hooks
import { useQED } from '../../main'
import { useFragment } from 'react-relay/hooks'


// the provider factory
export const Provider = ({ children }) => {
    // get the session manager
    const qed = useQED()
    // ask it for all known data readers and attach them as read-only state
    const { readers } = useFragment(graphql`
        fragment context_viz_connected_readers on QED {
            readers {
                id
                # and whatever else readers need
                ...context_viz_connected_reader
            }
        }`,
        qed
    )

    // build the initial context value
    const context = {
        // the data sources
        readers,
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
        // the set of known data sources
        readers: [],
    }
)


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viz' context: no provider"


// end of file
