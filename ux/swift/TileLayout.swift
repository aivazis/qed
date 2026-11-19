// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import CoreGraphics


/// Where the tiles of a dataset go on the screen at a zoom level
///
/// A level splits in two along each axis, as the web client's mosaic splits it. Its whole part,
/// when below zero, is the magnification: the server renders the dataset reduced by that many
/// powers of two. What is left is the distortion: the app resizes each tile by that power of two.
/// A level above zero is all distortion, so the app enlarges tiles the server renders at full size
struct TileLayout: Sendable {
    /// One tile and the rectangle it fills on the screen, in points
    struct Placement: Sendable, Hashable {
        let tile: Tile
        let frame: CGRect
    }

    // the size of the whole dataset on the screen
    let size: CGSize
    // the tiles that cover it
    let placements: [Placement]

    /// Lay out the tiles of the {channel} of {dataset}, shown by the view at {viewport}, at the
    /// zoom {level}, vertical first; {shape}, {origin} and {tile} are the dataset's, row first
    init(
        api: String, viewport: Int, dataset: String, channel: String, session: String,
        shape: [Int], origin: [Int], tile: [Int], level: [Double]
    ) {
        // split each axis into its run of tiles
        let rows = TileLayout.axis(extent: shape[0], origin: origin[0], tile: tile[0], level: level[0])
        let columns = TileLayout.axis(
            extent: shape[1], origin: origin[1], tile: tile[1], level: level[1])
        // the dataset on the screen is as large as its runs
        size = CGSize(width: columns.length, height: rows.length)
        // and every pairing of a run of rows with a run of columns is a tile
        placements = rows.segments.flatMap { row in
            columns.segments.map { column in
                Placement(
                    tile: Tile(
                        api: api, viewport: viewport, dataset: dataset, channel: channel,
                        session: session, level: [rows.magnification, columns.magnification],
                        origin: [row.origin, column.origin], shape: [row.extent, column.extent]),
                    frame: CGRect(
                        x: column.start, y: row.start, width: column.length, height: row.length))
            }
        }
    }

    /// The tiles that fill the rectangle {visible}, widened on every side by {margin} points
    func placements(in visible: CGRect, margin: CGFloat) -> [Placement] {
        // widen the rectangle, so tiles are on their way before they come into view
        let wanted = visible.insetBy(dx: -margin, dy: -margin)
        // and keep the tiles that meet it
        return placements.filter { $0.frame.intersects(wanted) }
    }

    /// One run of tiles along an axis: where the run starts and how long it is in pixels of the
    /// magnified dataset, and where it goes and how long it is on the screen
    struct Segment: Sendable, Equatable {
        let origin: Int
        let extent: Int
        let start: Double
        let length: Double
    }

    /// Split an axis of {extent} pixels that starts at {origin} into runs of {tile} pixels, at the
    /// zoom {level}; hand back the magnification the server renders, the runs, and the length of
    /// the axis on the screen
    static func axis(
        extent: Int, origin: Int, tile: Int, level: Double
    ) -> (magnification: Int, segments: [Segment], length: Double) {
        // the whole part of the level below zero is the server's, the rest is the app's; the
        // magnification is a reduction by a power of two, limited so it stays a whole number
        let whole = level > 0 ? 0 : max(Int(level.rounded(.towardZero)), -30)
        let magnification = -whole
        let distortion = pow(2.0, level - Double(whole))
        // the extent of the axis once the server has reduced it
        let reduced = extent >> magnification
        // cut it into runs of a tile, the last one taking whatever is left
        let segments = stride(from: 0, to: reduced, by: tile).map { start in
            Segment(
                origin: origin + start, extent: min(tile, reduced - start),
                start: Double(start) * distortion,
                length: Double(min(tile, reduced - start)) * distortion)
        }
        // all done
        return (magnification, segments, Double(reduced) * distortion)
    }
}


// end of file
