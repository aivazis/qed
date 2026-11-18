// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import SwiftUI


/// The application: a window on a qed server
@main
struct QEDApp: App {
    // the app's copy of the state of the server
    @State private var store: Store
    // the stream that keeps it current
    @State private var stream: EventStream

    /// Connect to the server
    init() {
        // while the app is being developed, the server is a qed on the same machine as the
        // simulator, which reaches it as {localhost}
        let server = Server(base: URL(string: "http://localhost:8005/")!)
        // keep a copy of its state
        let store = Store(client: Client(server: server))
        // and let its stream tell the copy when to catch up
        let stream = EventStream(server: server, listener: { notice in store.hear(notice) })
        // hold on to both for as long as the app runs
        _store = State(initialValue: store)
        _stream = State(initialValue: stream)
    }

    // the window and its contents
    var body: some Scene {
        WindowGroup {
            // show the link and the views, and follow the stream for as long as the window lives
            ConnectionView(stream: stream, store: store)
                .task { await stream.follow() }
        }
    }
}


// end of file
