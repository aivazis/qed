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

    // where the scroll view stands, so the app can move it
    @State private var position = ScrollPosition()
    // the part of the dataset on the screen, in points
    @State private var visible = CGRect.zero
    // what the scroll view is doing: still, under a finger, or coasting
    @State private var phase = ScrollPhase.idle
    // the level during a pinch, and until the server shows the one it ends with
    @State private var pinched: [Double]? = nil
    // the level when the pinch in progress started
    @State private var pinchStart: [Double]? = nil

    // how far beyond the screen tiles are fetched, so they are there before they are seen
    private let margin: CGFloat = 128
    // how far the server's center may be from where the app stands before the app moves to it;
    // a zoom leaves the two a fraction of a point apart
    private let drift: CGFloat = 2

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

    /// The tiles of {picture}, at the level of the pinch in progress or else the server's
    private func canvas(_ picture: Picture) -> some View {
        // the level the tiles are shown at
        let level = pinched ?? picture.level
        // where they go
        let layout = TileLayout(
            api: picture.api, viewport: viewport.index, dataset: picture.dataset,
            channel: picture.channel, session: picture.session, shape: picture.shape,
            origin: picture.origin, tile: picture.tile, level: level)
        // and which of them are on the screen, or nearly
        let shown = layout.placements(in: visible, margin: margin)
        // draw them
        return ScrollView([.horizontal, .vertical]) {
            ZStack(alignment: .topLeading) {
                ForEach(shown, id: \.tile) { placement in
                    TileImage(image: tiles.images[placement.tile])
                        .frame(width: placement.frame.width, height: placement.frame.height)
                        .offset(x: placement.frame.minX, y: placement.frame.minY)
                }
            }
            .frame(width: layout.size.width, height: layout.size.height, alignment: .topLeading)
        }
        .scrollPosition($position)
        // follow what the scroll view does
        .onScrollPhaseChange { _, now in phase = now }
        // as the part on the screen changes, record it, and when the change is the viewer's own
        // doing, move the view on the server along with it
        .onScrollGeometryChange(for: CGRect.self, of: { $0.visibleRect }) { _, now in
            visible = now
            if pinched == nil && (phase == .interacting || phase == .decelerating) {
                store.lookAt(
                    viewport: viewport.index,
                    row: now.midY / pow(2, level[0]), col: now.midX / pow(2, level[1]))
            }
        }
        // fetch the tiles on the screen, and let the rest go
        .onChange(of: shown.map(\.tile), initial: true) { _, wanted in
            tiles.want(wanted)
        }
        // stand where the server says the view is centered, once there is a screen to stand on,
        // and whenever the server's center or zoom changes
        .onChange(of: [picture.center.row, picture.center.col, level[0], level[1]]) {
            follow(picture, level: level)
        }
        .onChange(of: visible.size) { before, _ in
            if before == .zero {
                follow(picture, level: level)
            }
        }
        // a pinch zooms
        .simultaneousGesture(pinch(picture))
    }

    /// Scroll to the server's center of {picture} at {level}, unless the viewer is busy moving
    /// on its own, or is already there
    private func follow(_ picture: Picture, level: [Double]) {
        // leave the viewer alone while a finger moves it, a pinch zooms it, or a move of its own
        // is on its way to the server; and there is nowhere to stand without a screen
        guard
            phase == .idle, pinched == nil, !store.moving, visible.size != .zero
        else {
            return
        }
        // where the server's center puts the corner of the screen
        let target = CGPoint(
            x: picture.center.col * pow(2, level[1]) - visible.width / 2,
            y: picture.center.row * pow(2, level[0]) - visible.height / 2)
        // go there, unless the viewer is there already
        if hypot(target.x - visible.minX, target.y - visible.minY) > drift {
            position.scrollTo(point: target)
        }
    }

    /// The pinch: the picture follows the fingers, keeping the pixel at the center of the screen
    /// in place, and the level it ends at becomes the zoom of the view on the server
    private func pinch(_ picture: Picture) -> some Gesture {
        MagnifyGesture()
            .onChanged { value in
                // the level the pinch started from, and the level the picture shows now
                let shown = pinched ?? picture.level
                let start = pinchStart ?? shown
                pinchStart = start
                // the new level, within the range the web client allows
                let change = log2(value.magnification)
                let level = start.map { min(max($0 + change, -Double(picture.depth)), 4) }
                // the pixel at the center of the screen
                let row = visible.midY / pow(2, shown[0])
                let col = visible.midX / pow(2, shown[1])
                // show the new level, with that pixel still at the center
                pinched = level
                position.scrollTo(
                    point: CGPoint(
                        x: col * pow(2, level[1]) - visible.width / 2,
                        y: row * pow(2, level[0]) - visible.height / 2))
            }
            .onEnded { _ in
                // the pinch is over
                pinchStart = nil
                guard let level = pinched else {
                    return
                }
                // tell the server, and show its zoom once the copy has it
                Task {
                    await store.zoom(viewport: viewport.index, vertical: level[0], horizontal: level[1])
                    pinched = nil
                }
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


/// A tile, or the empty square that holds its place until it arrives
struct TileImage: View {
    // the image of the tile, once it is at hand
    let image: UIImage?

    // the contents
    var body: some View {
        if let image {
            Image(uiImage: image)
                .resizable()
        } else {
            Rectangle()
                .fill(.quaternary)
        }
    }
}


// end of file
