// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import SwiftUI


/// Show the tiles of a view; scrolling moves the view on the server, and a pinch zooms it, so
/// every client follows
struct Viewer: View {
    // the view, and its position among the server's views
    let viewport: Store.Viewport
    // the app's copy of the state of the server, which also carries the app's changes
    let store: Store
    // the tiles at hand
    let tiles: Tiles

    // the level a pinch ended at, until the server shows it
    @State private var pinched: [Double]? = nil

    // how far beyond the screen tiles are fetched, so they are there before they are seen
    private let margin: CGFloat = 128

    // the contents
    var body: some View {
        if let picture = Picture(viewport.view) {
            canvas(picture)
        } else {
            ContentUnavailableView(
                "Nothing to show", systemImage: "photo",
                description: Text("The view has no dataset yet."))
        }
    }

    /// The tiles of {picture}, at the level a pinch ended at or else the server's
    private func canvas(_ picture: Picture) -> some View {
        // the level the tiles are laid out at
        let level = pinched ?? picture.level
        // where they go
        let layout = TileLayout(
            api: picture.api, viewport: viewport.index, dataset: picture.dataset,
            channel: picture.channel, session: picture.session, shape: picture.shape,
            origin: picture.origin, tile: picture.tile, level: level)
        // draw them; the canvas follows the server's center unless a change of the app's own
        // is on its way there, and the tiles it wants are fetched while the rest are let go
        return Canvas(
            layout: layout, images: tiles.images,
            level: level, range: -Double(picture.depth)...4,
            center: picture.center, follow: pinched == nil && !store.moving, margin: margin,
            wanted: { wanted in tiles.want(wanted) },
            moved: { row, col in store.lookAt(viewport: viewport.index, row: row, col: col) },
            zoomed: { level in zoom(to: level) }
        )
    }

    /// Show {level} right away, tell the server, and go back to the server's level once the
    /// copy shows it
    private func zoom(to level: [Double]) {
        pinched = level
        Task {
            await store.zoom(viewport: viewport.index, vertical: level[0], horizontal: level[1])
            pinched = nil
        }
    }
}


/// What the viewer needs from a view to show it; a view that lacks any of it shows nothing
struct Picture {
    // the path of its tiles, its dataset, the channel it shows, and its session
    let api: String
    let dataset: String
    let channel: String
    let session: String
    // the shape, origin and tile of its dataset, row first
    let shape: [Int]
    let origin: [Int]
    let tile: [Int]
    // its zoom level along each axis, vertical first, and how far it can zoom out
    let level: [Double]
    let depth: Int
    // the pixel of its dataset at its center
    let center: (row: Double, col: Double)

    /// Extract what the viewer needs from {view}, if it is all there
    init?(_ view: StateQuery.View) {
        // the parts that name the tiles
        guard
            let api = view.reader?.api, let dataset = view.dataset?.name,
            let channel = view.channel?.tag, let session = view.session,
            let shape = Picture.pair(view.dataset?.shape), let tile = Picture.pair(view.dataset?.tile)
        else {
            return nil
        }
        self.api = api
        self.dataset = dataset
        self.channel = channel
        self.session = session
        self.shape = shape
        self.tile = tile
        // the dataset starts at its corner unless it says otherwise
        origin = Picture.pair(view.dataset?.origin) ?? [0, 0]
        // a view without a zoom shows its dataset pixel for pixel
        level = [view.zoom?.vertical ?? 0, view.zoom?.horizontal ?? 0]
        depth = view.depth ?? 0
        // and one without a center looks at the middle of its dataset
        center = (
            row: view.center?.row ?? Double(shape[0]) / 2,
            col: view.center?.col ?? Double(shape[1]) / 2
        )
    }

    /// A pair of numbers, if {values} holds exactly two of them
    private static func pair(_ values: [Int?]?) -> [Int]? {
        let numbers = (values ?? []).compactMap { $0 }
        return numbers.count == 2 ? numbers : nil
    }
}


// end of file
