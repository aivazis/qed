// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


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
    // hand back a teardown that closes the stream
    return () => source.close()
}


// end of file
