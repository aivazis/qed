// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { useEffect } from 'react'


// register a {listener} with {client} for the given event {name} that gets updated
// whenever {triggers} are modified
export const useEvent = ({
    name = throwError(), listener = null, client = null, triggers = null
}) => {
    // create an effect
    useEffect(() => {
        // if there is no listener or no client
        if (listener == null || client == null) {
            // bail
            return
        }
        // figure out the effect target
        const target = client.current || window
        // add {listener} as an event listener
        target.addEventListener(name, listener)
        // make a controller; not sure whether this is required, useful, harmful...
        const controller = new AbortController()
        // and register a clean up
        return () => {
            // that removes the listener
            target.removeEventListener(name, listener)
            // and aborts any pending requests
            controller.abort()
        }
    },
        // register the refresh {triggers}
        triggers
    )
    // all done
    return
}


// end of file
