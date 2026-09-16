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
        // relay hands an identical request that arrives while one is in flight the response of
        // the one in flight, which was computed before the change that prompted the new request,
        // so a change frame that lands mid-refetch would be lost; instead, remember that one
        // arrived and refetch once more when the current one settles
        let inflight = null
        let again = false
        const refetch = () => {
            // a refetch under way absorbs this request
            if (inflight) {
                // but leaves a note to go again
                again = true
                // all done
                return inflight
            }
            // otherwise, fetch
            inflight = fetchQuery(
                environment, stateQuery, {}, { fetchPolicy: "network-only" },
            ).toPromise().finally(() => {
                // the fetch has settled
                inflight = null
                // if a change arrived in the meantime
                if (again) {
                    // clear the note
                    again = false
                    // and catch up
                    refetch()
                }
            })
            // hand back the promise
            return inflight
        }
        // wire the portable event stream to the refetch and hand back its teardown
        return subscribe(refetch)
    }, [])
    // render nothing
    return null
}


// end of file
