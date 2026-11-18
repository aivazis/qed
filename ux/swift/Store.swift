// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Observation


/// The app's copy of the state of a qed server, kept current by what its event stream says
///
/// A change names nothing, so every change, and every reconnection after which changes may have
/// gone unannounced, is answered by asking for the whole state again. A greeting from a run of
/// the server other than the one the copy came from makes the copy worthless
@MainActor
@Observable
final class Store {
    // the views of the server
    private(set) var views: [StateQuery.View] = []
    // why the last attempt to read the state failed, if it did
    private(set) var problem: String? = nil

    // the client that asks the server
    private let client: Client
    // the run of the server the copy came from
    private var instance: String? = nil
    // whether a request for the state is in flight
    private var asking = false
    // whether the state changed since the request in flight was made
    private var stale = false

    /// Keep a copy of the state of the server that {client} talks to
    init(client: Client) {
        // record the client
        self.client = client
    }

    /// Respond to what the event stream says
    func hear(_ notice: EventStream.Notice) {
        switch notice {
        // after a reconnection, or a change, the copy is out of date
        case .opened, .changed:
            refresh()
        // a run of the server other than the known one makes the copy worthless
        case .greeted(let run):
            if let known = instance, known != run {
                views = []
                refresh()
            }
            instance = run
        }
    }

    /// Bring the copy up to date; requests made while one is in flight fold into a single one
    /// that follows it
    func refresh() {
        // mark the copy out of date
        stale = true
        // if a request is already in flight, the one that follows it will catch up
        guard !asking else {
            return
        }
        // otherwise, ask
        asking = true
        Task {
            await ask()
        }
    }

    /// Ask for the state for as long as it keeps changing while the answers are on their way
    private func ask() async {
        while stale {
            // this request covers every change so far
            stale = false
            do {
                // ask, and keep the views that are there
                let answer = try await client.run(StateQuery.operation)
                views = (answer.qed?.views ?? []).compactMap { $0 }
                problem = nil
            } catch {
                // keep what we had, and say why it could not be brought up to date
                problem = String(describing: error)
            }
        }
        // nothing is in flight anymore
        asking = false
    }
}


// end of file
