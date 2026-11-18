// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Foundation
import Observation


/// The event stream of a qed server: follow it for as long as the app runs, keep track of the
/// state of the link, the run of the server on the other end, and the changes it announces, and
/// tell a listener about each of them
@MainActor
@Observable
final class EventStream {
    /// The state of the link to the server
    enum Link: Sendable {
        // asking for the stream
        case connecting
        // the stream is flowing
        case open
        // the stream was refused or broke off; another attempt follows
        case lost
    }

    /// What the stream tells its listener
    enum Notice: Sendable, Equatable {
        // the stream is flowing again; whatever happened while it was not went unannounced
        case opened
        // the server named the run on the other end, if its greeting could be read
        case greeted(String?)
        // the server announced a change of its state
        case changed
    }

    // the server whose stream this is
    let server: Server
    // the state of the link
    private(set) var link = Link.connecting
    // the run of the server on the other end, as its greeting names it
    private(set) var instance: String? = nil
    // how many changes the server announced since the app started
    private(set) var changes = 0

    // who hears about what the stream says
    private let listener: @MainActor (Notice) -> Void
    // the shortest and longest waits between attempts to reconnect
    private let shortest = 1.0
    private let longest = 30.0

    /// Follow the stream of {server}, and tell {listener} what it says
    init(server: Server, listener: @escaping @MainActor (Notice) -> Void = { _ in }) {
        // record the server
        self.server = server
        // and the listener
        self.listener = listener
    }

    /// Follow the stream until the task that runs this is cancelled, reconnecting whenever the
    /// link is lost, and waiting longer after each failure until a connection holds
    func follow() async {
        // start with the shortest wait
        var wait = shortest
        // for as long as the app wants the stream
        while !Task.isCancelled {
            // ask for it
            link = .connecting
            do {
                // and read it until it ends or fails; a stream that opens resets the wait
                try await EventStream.read(
                    server: server,
                    opened: { await self.opened() },
                    receive: { frame in await self.receive(frame) })
                wait = shortest
            } catch {
                // a failure is reported through the state of the link; there is nothing else to
                // do about it but try again
            }
            // the link is gone
            link = .lost
            // wait before trying again, and wait longer next time
            try? await Task.sleep(for: .seconds(wait))
            wait = min(2 * wait, longest)
        }
        // all done
        return
    }

    /// Read the stream of {server}, report when it opens, and hand each frame to {receive}
    nonisolated private static func read(
        server: Server,
        opened: @Sendable () async -> Void,
        receive: @Sendable (Frame) async -> Void
    ) async throws {
        // ask for the stream, as a stream; proxies on the way hold anything else until it ends
        let request = server.request(for: "events", accept: "text/event-stream")
        let (bytes, response) = try await URLSession.shared.bytes(for: request)
        // anything other than a plain success means there is no stream
        guard let status = (response as? HTTPURLResponse)?.statusCode, status == 200 else {
            throw URLError(.badServerResponse)
        }
        // the stream is flowing
        await opened()
        // cut it into frames as the bytes arrive, and pass each one on
        var reader = FrameReader()
        for try await byte in bytes {
            if let frame = reader.consume(byte) {
                await receive(frame)
            }
        }
        // the server ended the stream
        return
    }

    /// Note that the stream is flowing
    private func opened() {
        // the link is up
        link = .open
        // say so
        listener(.opened)
    }

    /// Take in a {frame} from the server
    private func receive(_ frame: Frame) {
        // the greeting names the run of the server; anything else announces a change
        switch frame.event {
        case "hello":
            instance = EventStream.instance(in: frame.data)
            listener(.greeted(instance))
        default:
            changes += 1
            listener(.changed)
        }
    }

    /// Extract the name of the run of the server from the {data} of its greeting
    private static func instance(in data: String) -> String? {
        // the greeting is a small json document with the name under {instance}
        struct Greeting: Decodable {
            let instance: String
        }
        // a greeting that cannot be read names nothing
        return try? JSONDecoder().decode(Greeting.self, from: Data(data.utf8)).instance
    }
}


// end of file
