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
    // the kinds of change with one in flight
    private var busy: Set<String> = []
    // the latest change of each kind asked for while one of its kind was in flight
    private var next: [String: () async throws -> Void] = [:]

    // whether a move of a view is in flight
    var moving: Bool {
        busy.contains("lookAt")
    }

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

    /// Send the change {work} of the {kind}, paced: at most one change of a kind is in flight,
    /// the latest one asked for while it is waits behind it, and the ones in between are dropped
    ///
    /// A finger moves a view or a slider far faster than the server answers, and only where it
    /// comes to rest matters, so that one is never dropped
    func pace(_ kind: String, _ work: @escaping () async throws -> Void) {
        // if a change of this kind is in flight, this one is next
        guard !busy.contains(kind) else {
            next[kind] = work
            return
        }
        // otherwise, send it
        busy.insert(kind)
        Task {
            await send(kind, work)
        }
    }

    /// Send {work}, and then whatever change of the same {kind} was asked for while it was on
    /// its way
    private func send(_ kind: String, _ work: @escaping () async throws -> Void) async {
        // send changes until none are waiting
        var pending: (() async throws -> Void)? = work
        while let current = pending {
            do {
                try await current()
            } catch {
                // say why the change failed, and go on to the next one regardless, so a passing
                // failure does not strand the view where it was
                problem = String(describing: error)
            }
            // take the next one, if any
            pending = next.removeValue(forKey: kind)
        }
        // nothing of this kind is in flight anymore
        busy.remove(kind)
    }

    /// Send {input} to the server through {mutation} right away, reporting a failure
    private func change<Input, Answer>(_ mutation: Mutation<Input, Answer>, _ input: Input) {
        Task {
            do {
                _ = try await client.run(mutation, input: input)
            } catch {
                problem = String(describing: error)
            }
        }
    }

    /// Put the pixel at {row} and {col} of its dataset at the center of the view at {viewport}
    func lookAt(viewport: Int, row: Double, col: Double) {
        let input = ViewMutations.LookAt(viewport: viewport, row: row, col: col)
        pace("lookAt") { [client] in
            _ = try await client.run(ViewMutations.lookAt, input: input)
        }
    }

    /// Set the zoom of the view at {viewport} to {vertical} and {horizontal} as a slider moves
    func slideZoom(viewport: Int, vertical: Double, horizontal: Double) {
        let input = ViewMutations.SetZoom(viewport: viewport, vertical: vertical, horizontal: horizontal)
        pace("zoom") { [client] in
            _ = try await client.run(ViewMutations.setZoom, input: input)
        }
    }

    /// Let the zoom of the view at {viewport} move along both axes together, or each on its own
    func toggleCoupled(viewport: Int) {
        change(ViewMutations.toggleCoupled, ViewMutations.Viewport(viewport: viewport))
    }

    /// Put the zoom of the view at {viewport} back where it started
    func resetZoom(viewport: Int) {
        change(ViewMutations.resetZoom, ViewMutations.Viewport(viewport: viewport))
    }

    /// Show the channel {tag} of the dataset of {reader} in the view at {viewport}
    func setChannel(viewport: Int, reader: String, tag: String) {
        change(ViewMutations.setChannel, ViewMutations.SetChannel(viewport: viewport, reader: reader, value: tag))
    }

    /// Set a range controller as {input} says, as a slider moves
    func setRange(_ input: ViewMutations.SetRange) {
        pace("range.\(input.controller)") { [client] in
            _ = try await client.run(ViewMutations.setRange, input: input)
        }
    }

    /// Set a value controller as {input} says, as a slider moves
    func setValue(_ input: ViewMutations.SetValue) {
        pace("value.\(input.controller)") { [client] in
            _ = try await client.run(ViewMutations.setValue, input: input)
        }
    }

    /// Let a controller follow the data, or hold it where it is
    func setAuto(_ input: ViewMutations.SetAuto, range: Bool) {
        change(range ? ViewMutations.setRangeAuto : ViewMutations.setValueAuto, input)
    }

    /// Put a controller back where it started
    func reset(_ input: ViewMutations.Slot, range: Bool) {
        change(range ? ViewMutations.resetRange : ViewMutations.resetValue, input)
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
