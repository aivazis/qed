// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// the provider factory
export const Provider = ({ children }) => {
    // the current documentation topic
    const [topic, setTopic] = React.useState("intro")
    // the activity panel visibility flag
    const [activityPanel, setActivityPanel] = React.useState(true)

    // build the current value of the context
    const context = {
        // the help topic
        topic, setTopic,
        // the activity panel state flag and its mutator
        activityPanel, setActivityPanel,
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
        // the help topic
        topic: null,
        setTopic: () => { throw new Error(complaint) },
        // the activity panel state and its mutator
        activityPanel: null,
        setActivityPanel: () => { throw new Error(complaint) },
    }
)

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'main' context: no provider"


// end of file
