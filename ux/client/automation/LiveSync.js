// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { useEffect } from 'react'
// relay
import { fetchQuery } from 'react-relay'

// local
import { environment } from '../environment'
import { query as stateQuery } from '../context/useFetchQED'
import { subscribe } from './eventStream'


// keep this client in step with the server: on every pushed event, refetch the application state so
// a change made by any other client (or by automation) is reflected here without polling. it renders
// nothing; mounting it ties the subscription to the app lifecycle
export const LiveSync = () => {
    // on mount
    useEffect(() => {
        // RELAY-SPECIFIC -- swap this body for the Houdini equivalent on migration; everything else
        // in this feature is plain DOM. refetch the top-level state query straight from the network,
        // which updates the relay store and re-renders every component reading from it
        const refetch = () => fetchQuery(
            environment, stateQuery, {}, { fetchPolicy: "network-only" },
        ).toPromise()
        // wire the portable event stream to the refetch and hand back its teardown
        return subscribe(refetch)
    }, [])
    // render nothing
    return null
}


// end of file
