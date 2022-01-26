// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// hooks
import { useFetchServerVersion } from './useFetchServerVersion'


// the provider factory
export const Provider = ({ children }) => {
    // ask the server for its version
    const info = useFetchServerVersion()
    // and attach it as read-only state
    const [serverVersion] = React.useState(info)

    // make a slot for the time of the last response from the server
    const [heartbeat, setHeartbeat] = React.useState(new Date())

    // build the initial context value
    const context = {
        // the server version
        serverVersion,
        // the heartbeat
        heartbeat, setHeartbeat,
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
        // the server version
        serverVersion: null,
        // the timestamp of the last time we checked in with the server
        heartbeat: null,
        setHeartbeat: () => { throw new Error(complaint) },
    }
)


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'qed' context: no provider"


// end of file
