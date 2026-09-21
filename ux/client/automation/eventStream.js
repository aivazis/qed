// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// local
import { instance } from './instance'
import { reachability } from './reachability'


// open the server's event stream and invoke {onChange} on every pushed event
//
// this is pure DOM: it knows nothing about the GraphQL client and survives the Relay -> Houdini
// migration untouched. the one client-specific atom, "given an event, refetch the affected state",
// is supplied by the caller as {onChange}
export const subscribe = (onChange) => {
    // subscribe to the server-sent event stream; the server holds this connection open and pushes
    // a frame whenever its state changes. {EventSource} reconnects on its own if the link drops
    const source = new EventSource("events")
    // on each pushed event, let the caller react
    source.onmessage = () => { onChange() }
    // the stream is up. this fires on the first connection and on every reconnection the
    // browser makes on its own, and the two cases want the same thing: whatever the server
    // did while we were not listening never arrived as an event, so the only way to find out
    // is to ask again. without this, a client that loses its server and gets it back carries
    // on showing what it knew beforehand until some later event happens to land
    source.onopen = () => {
        // we are in touch
        reachability.reached()
        // and out of date by however long we were away
        onChange()
        // all done
        return
    }
    // every stream opens with a greeting that says which run of the server is on the other
    // end. it has a name of its own, so it does not arrive as a message, and the refetch that
    // {onopen} started is wasted only when it turns out to be a stranger
    source.addEventListener("hello", e => {
        // carefully, since the payload comes from the network
        try {
            // find out who it is; a stranger makes the page start over
            instance.greet(JSON.parse(e.data).instance)
        } catch (error) {
            // a greeting that cannot be read tells us nothing, which is what we knew before
            console.error("events: undecodable greeting", error)
        }
        // all done
        return
    })
    // the stream is down: the connection dropped, or the server is not answering. the browser
    // retries by itself every few seconds and will report success through {onopen}; until then
    // everything this client displays is as old as the last frame it received, and it says so
    source.onerror = () => {
        // note it; repeated failures settle to the same standing and go unremarked
        reachability.lost()
        // all done
        return
    }
    // hand back a teardown that closes the stream
    return () => source.close()
}


// end of file
