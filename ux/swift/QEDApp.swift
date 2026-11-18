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
    // the stream of the server; while the app is being developed, that is a qed on the same
    // machine as the simulator, which reaches it as {localhost}
    @State private var stream = EventStream(
        server: Server(base: URL(string: "http://localhost:8005/")!))

    // the window and its contents
    var body: some Scene {
        WindowGroup {
            // show the state of the link, and follow the stream for as long as the window lives
            ConnectionView(stream: stream)
                .task { await stream.follow() }
        }
    }
}


// end of file
