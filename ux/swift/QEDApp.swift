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
    // the tiles at hand
    @State private var tiles: Tiles

    /// Connect to the server
    init() {
        // while the app is being developed, the server is a qed on the same machine as the
        // simulator, which reaches it as {localhost}
        let server = Server(base: URL(string: "http://localhost:8005/")!)
        // keep a copy of its state
        let store = Store(client: Client(server: server))
        // and let its stream tell the copy when to catch up
        let stream = EventStream(server: server, listener: { notice in store.hear(notice) })
        // hold on to both for as long as the app runs, along with the tiles it fetches
        _store = State(initialValue: store)
        _stream = State(initialValue: stream)
        _tiles = State(initialValue: Tiles(server: server))
    }

    // the window and its contents
    var body: some Scene {
        WindowGroup {
            // the server and its views beside the view on the screen; follow the stream for as
            // long as the window lives
            ServerWindow(stream: stream, store: store, tiles: tiles)
                .task { await stream.follow() }
        }
    }
}


/// The window: the server and its views in a sidebar, and the view the iPad shows beside it
struct ServerWindow: View {
    // the stream of the server
    let stream: EventStream
    // the app's copy of its state
    let store: Store
    // the tiles at hand
    let tiles: Tiles

    // the position of the view on the screen; the iPad picks its own, starting with the first
    @State private var active = 0
    // whether the controls of the view are on the screen
    @State private var controls = false

    // the contents; the sidebar and the controls slide over the view, which stays where it is
    var body: some View {
        NavigationSplitView {
            ConnectionView(stream: stream, store: store, active: $active)
        } detail: {
            if let viewport = store.views.first(where: { $0.index == active }) {
                // the view, with its controls over its trailing edge when they are asked for
                Viewer(viewport: viewport, store: store, tiles: tiles)
                    .overlay(alignment: .trailing) {
                        if controls {
                            Controls(viewport: viewport, store: store)
                                .scrollContentBackground(.hidden)
                                .frame(width: 340)
                                .background(.regularMaterial)
                                .transition(.move(edge: .trailing))
                        }
                    }
                    .animation(.default, value: controls)
                    .navigationTitle(viewport.view.reader?.name ?? viewport.view.name)
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        Button("Controls", systemImage: "slider.horizontal.3") {
                            controls.toggle()
                        }
                    }
            } else {
                ContentUnavailableView(
                    "No view", systemImage: "rectangle.dashed",
                    description: Text("The server has no view to show."))
            }
        }
        .navigationSplitViewStyle(.prominentDetail)
    }
}


// end of file
