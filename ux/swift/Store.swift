// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Observation


/// The app's copy of the state of a qed server, kept current by what its event stream says, and
/// the changes the app makes to that state
///
/// A change names nothing, so every change, and every reconnection after which changes may have
/// gone unannounced, is answered by asking for the whole state again. A greeting from a run of
/// the server other than the one the copy came from makes the copy worthless. The app's own
/// changes come back the same way, through the stream
@MainActor
@Observable
final class Store {
    /// A view of the server and its position among the server's views, which is how tiles and
    /// changes name it
    struct Viewport: Sendable {
        let index: Int
        let view: StateQuery.View
    }

    // the views of the server
    private(set) var views: [Viewport] = []
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
    // whoever is waiting for the copy to catch up
    private var waiting: [CheckedContinuation<Void, Never>] = []
    // whether a move of a view is in flight
    private(set) var moving = false
    // the latest move asked for while one was in flight
    private var nextMove: ViewMutations.LookAt? = nil

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
                // ask, and keep the views that are there, each with its position among them
                let answer = try await client.run(StateQuery.operation)
                views = (answer.qed?.views ?? []).enumerated().compactMap { index, view in
                    view.map { Viewport(index: index, view: $0) }
                }
                problem = nil
            } catch {
                // keep what we had, and say why it could not be brought up to date
                problem = String(describing: error)
            }
        }
        // nothing is in flight anymore
        asking = false
        // and the copy has caught up with every change so far
        let caughtUp = waiting
        waiting.removeAll()
        caughtUp.forEach { $0.resume() }
    }

    /// Wait until the copy has caught up with the state of the server as it is now
    func catchUp() async {
        // ask for the state, and wait for the answer to land
        await withCheckedContinuation { continuation in
            waiting.append(continuation)
            refresh()
        }
    }

    /// Put the pixel at {row} and {col} of its dataset at the center of the view at {viewport}
    ///
    /// Moves come far faster than the server answers, so at most one is in flight; the latest
    /// one asked for while it is waits behind it, and the ones in between are dropped
    func lookAt(viewport: Int, row: Double, col: Double) {
        // the move
        let move = ViewMutations.LookAt(viewport: viewport, row: row, col: col)
        // if one is in flight, this one is next
        guard !moving else {
            nextMove = move
            return
        }
        // otherwise, send it
        moving = true
        Task {
            await send(move)
        }
    }

    /// Send {move}, and then whatever move was asked for while it was on its way
    private func send(_ move: ViewMutations.LookAt) async {
        // send moves until none are waiting
        var pending: ViewMutations.LookAt? = move
        while let current = pending {
            do {
                _ = try await client.run(ViewMutations.lookAt, input: current)
            } catch {
                // say why the move failed, and go on to the next one regardless, so a passing
                // failure does not strand the view where it was
                problem = String(describing: error)
            }
            // take the next one, if any
            pending = nextMove
            nextMove = nil
        }
        // nothing is in flight anymore
        moving = false
    }

    /// Set the zoom of the view at {viewport} to the levels {vertical} and {horizontal}, and come
    /// back once the copy shows it
    func zoom(viewport: Int, vertical: Double, horizontal: Double) async {
        // ask for the change
        do {
            let input = ViewMutations.SetZoom(
                viewport: viewport, vertical: vertical, horizontal: horizontal)
            _ = try await client.run(ViewMutations.setZoom, input: input)
        } catch {
            // say why it failed; the copy shows the zoom the server kept
            problem = String(describing: error)
        }
        // and wait for the copy to show what the server did with it
        await catchUp()
    }
}


// end of file
