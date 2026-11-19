// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Foundation
import Observation
import UIKit


/// Fetch the tiles the viewer wants from the server, and keep the most recent ones
@MainActor
@Observable
final class Tiles {
    // the images of the tiles at hand
    private(set) var images: [Tile: UIImage] = [:]

    // the server that renders them
    private let server: Server
    // the tiles at hand, from the least to the most recently wanted
    private var recent: [Tile] = []
    // the tiles on their way, and the work that brings each one
    private var arriving: [Tile: Task<Void, Never>] = [:]
    // how many tiles to keep; a tile takes about 768 KB once decoded
    private let capacity = 256

    /// Fetch tiles from {server}
    init(server: Server) {
        // record the server
        self.server = server
    }

    /// Make sure the {wanted} tiles are at hand or on their way, and stop fetching any others
    func want(_ wanted: [Tile]) {
        // the tiles still on their way that nobody wants anymore are abandoned
        let keep = Set(wanted)
        for (tile, work) in arriving where !keep.contains(tile) {
            work.cancel()
            arriving[tile] = nil
        }
        // every wanted tile is either at hand, and becomes the most recent, or is sent for
        for tile in wanted {
            if images[tile] != nil {
                touch(tile)
            } else if arriving[tile] == nil {
                arriving[tile] = Task { await fetch(tile) }
            }
        }
    }

    /// Fetch {tile} and keep it
    private func fetch(_ tile: Tile) async {
        // bring it over and decode it, away from the main actor
        let image = try? await Tiles.download(tile, from: server)
        // a tile that was abandoned on the way is someone else's business by now
        guard !Task.isCancelled else {
            return
        }
        // otherwise it is no longer on its way, so a tile that did not arrive is asked for again
        // the next time it is wanted
        arriving[tile] = nil
        // and one that did is kept, as the most recent tile
        guard let image else {
            return
        }
        images[tile] = image
        touch(tile)
        // and make room by letting go of the least recent ones
        while recent.count > capacity {
            images[recent.removeFirst()] = nil
        }
    }

    /// Mark {tile} as the most recently wanted
    private func touch(_ tile: Tile) {
        recent.removeAll { $0 == tile }
        recent.append(tile)
    }

    /// Fetch {tile} from {server} and decode it, so it is ready to be drawn
    nonisolated private static func download(_ tile: Tile, from server: Server) async throws -> UIImage? {
        // ask for it
        let request = server.request(for: tile.path, query: tile.query)
        let (data, response) = try await URLSession.shared.data(for: request)
        // anything other than a plain success is not a tile
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            return nil
        }
        // decode it now, so drawing it costs nothing
        return await UIImage(data: data)?.byPreparingForDisplay()
    }
}


// end of file
