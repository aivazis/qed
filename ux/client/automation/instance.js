// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// which run of the server this client is talking to
//
// every event stream opens with a greeting that carries a token the server mints when it
// starts. the browser reconnects a dropped stream on its own, and nothing about a reconnection
// says whether the same server answered: it may have been restarted, or replaced by another
// one on the same port, with different data, a different schema, and a different client to
// serve. the token is how this client finds out
//
// this is plain dom, with no react in it, so every stream can use it


// local
import { startOver } from './startOver'


// the token of the server this page was loaded against; unknown until the first greeting
let known = null


// the store
export const instance = {
    // the token of the server we know, if we have been greeted
    token: () => known,

    // a stream has been greeted by the server that carries {token}
    greet: token => {
        // a greeting without a token comes from a server that does not mint them
        if (!token) {
            // so there is nothing to compare
            return
        }
        // the first greeting is the introduction
        if (known === null) {
            // remember who this is
            known = token
            // all done
            return
        }
        // the server we know, back after a dropped connection, is no news
        if (known === token) {
            // so carry on
            return
        }
        // otherwise, somebody else is on the other end. everything this page holds describes
        // a server that is gone: the records in the relay store, whose ids the new server is
        // free to reuse for other things, the local edits made on its behalf, and possibly the
        // code of the page itself. start over, against whoever is there now
        startOver()
        // all done
        return
    },
}


// end of file
