// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Foundation


/// A tile of a view: the part of its dataset at one magnification that the server renders as one
/// image
struct Tile: Hashable, Sendable {
    // the path under which the server serves tiles of the view's reader
    let api: String
    // the position of the view among the server's views
    let viewport: Int
    // the dataset and the channel of it the view shows
    let dataset: String
    let channel: String
    // the session of the view
    let session: String
    // the magnification, as a whole level along each axis, vertical first
    let level: [Int]
    // the first pixel of the tile and its shape, in pixels of the magnified dataset, row first
    let origin: [Int]
    let shape: [Int]

    /// The path of the tile, below the address of the server
    var path: String {
        // the parts, in the order the server reads them
        let parts = [
            api, String(viewport), dataset, channel,
            level.map(String.init).joined(separator: "x"),
            origin.map(String.init).joined(separator: "x") + "+"
                + shape.map(String.init).joined(separator: "x"),
        ]
        // all done
        return parts.joined(separator: "/")
    }

    /// The parameters that go with the path
    var query: [URLQueryItem] {
        [URLQueryItem(name: "session", value: session)]
    }
}


// end of file
