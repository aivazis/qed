// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// whether this client is in touch with its server
//
// the event stream is the only connection a client holds open, so it is also the only place
// that finds out promptly when the server goes away: the browser notices within a few seconds
// and retries on its own, forever, without telling anybody. this store is where that news is
// put so the rest of the client can act on it
//
// this is plain dom, with no react in it, matching the journal store


// the states, which are also the names of the paint the status bar carries for each
const unknown = "unknown"
const good = "good"
const error = "error"

// the current standing, as a stable reference; replaced only when the standing changes, so a
// snapshot is safe to hand to {useSyncExternalStore}
let snapshot = { state: unknown, since: null }
// the listeners to notify on change
const listeners = new Set()


// notify everybody
const notify = () => {
    // go through the listeners
    for (const listener of listeners) {
        // and poke each one
        listener()
    }
    // all done
    return
}

// move to {state}, if that is not where we already are
const settle = state => {
    // a report that agrees with what we believe changes nothing, and must not, or every
    // failed reconnect attempt would re-render the client
    if (snapshot.state === state) {
        // so leave
        return
    }
    // otherwise, this is a transition; stamp it, so whoever displays it can say since when
    snapshot = { state, since: new Date() }
    // and let everybody know
    notify()
    // all done
    return
}


// the store
export const reachability = {
    // the current standing
    state: () => snapshot,

    // the stream is open: we are in touch
    reached: () => settle(good),

    // the stream is down: the browser is retrying, and until it succeeds anything this
    // client believes about the server is only as fresh as the last frame it received
    lost: () => settle(error),

    // register {listener} for changes; returns the matching teardown
    subscribe: listener => {
        // add the listener
        listeners.add(listener)
        // hand back the teardown
        return () => {
            // remove the listener
            listeners.delete(listener)
            // all done
            return
        }
    },
}


// end of file
