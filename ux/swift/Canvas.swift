// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import SwiftUI
import UIKit


/// The surface the tiles of a view are drawn on: UIKit's scroll view, which pans and zooms with
/// one gesture, zooming about the point between the fingers
///
/// While a pinch is in progress, the scroll view scales the tiles already on the screen. When
/// it ends, the scale becomes a zoom level, which the canvas reports; the viewer then lays the
/// tiles out at that level, and the canvas puts its scale back to one without moving what is on
/// the screen. The canvas works out which tiles are on the screen itself, since it is the one
/// that knows, and asks the viewer for them
struct Canvas: UIViewRepresentable {
    // where the tiles go at the current level
    let layout: TileLayout
    // the images of the tiles at hand
    let images: [Tile: UIImage]
    // the zoom level of the layout, vertical first, and the range a pinch may take it through
    let level: [Double]
    let range: ClosedRange<Double>
    // the pixel of the dataset the server has at the center of the view, and whether the canvas
    // may move to it now
    let center: (row: Double, col: Double)
    let follow: Bool
    // how far beyond the screen tiles are wanted, so they are there before they are seen
    let margin: CGFloat
    // what the canvas reports: the tiles it wants, the pixel of the dataset that a finger brought
    // to the center, and the level a pinch ended at
    let wanted: ([Tile]) -> Void
    let moved: (_ row: Double, _ col: Double) -> Void
    let zoomed: ([Double]) -> Void

    /// Make the scroll view and the view that holds the tiles
    func makeUIView(context: Context) -> UIScrollView {
        // the scroll view, which reports what it does to the coordinator
        let scroller = LayingOut()
        scroller.delegate = context.coordinator
        scroller.bouncesZoom = true
        scroller.contentInsetAdjustmentBehavior = .never
        // the view the tiles are placed in, and the one the scroll view zooms
        scroller.addSubview(context.coordinator.content)
        // once the scroll view knows its size, the tiles on the screen are known too
        scroller.laidOut = { [weak coordinator = context.coordinator] scroller in
            coordinator?.laidOut(scroller)
        }
        // all done
        return scroller
    }

    /// Bring the scroll view up to date with the layout, the tiles and the server
    func updateUIView(_ scroller: UIScrollView, context: Context) {
        context.coordinator.update(self, scroller: scroller)
    }

    /// Make the object that keeps track of the scroll view
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    /// The scroll view, which says when it has been laid out
    final class LayingOut: UIScrollView {
        // whom to tell
        var laidOut: ((UIScrollView) -> Void)? = nil

        /// Lay out, and say so
        override func layoutSubviews() {
            super.layoutSubviews()
            laidOut?(self)
        }
    }

    /// Keep track of the scroll view: place the tiles, apply changes of level, follow the server,
    /// and report what the person holding the iPad does
    @MainActor
    final class Coordinator: NSObject, UIScrollViewDelegate {
        // the view that holds the tiles
        let content = UIView()
        // the view of each tile placed at the current level
        private var views: [Tile: UIImageView] = [:]
        // the views of tiles that are no longer placed, from a previous level or a previous
        // rendering, kept underneath until what took their place has arrived, so a change of
        // level or of rendering never shows an empty screen
        private var retiring: [Tile: UIImageView] = [:]
        // the most recent description of the canvas
        private var canvas: Canvas? = nil
        // the level the content is laid out at
        private var applied: [Double]? = nil
        // the tiles last asked for
        private var asked: [Tile] = []
        // the size the scroll view had when it was last laid out
        private var laid = CGSize.zero

        /// Bring {scroller} up to date with {canvas}
        func update(_ canvas: Canvas, scroller: UIScrollView) {
            // remember it, so the reports go to the current owner
            self.canvas = canvas
            // a new level, from the end of a pinch or from the server, takes the place of the
            // old one with the pixel at the center of the screen held in place
            if applied != canvas.level {
                relevel(scroller, to: canvas)
            }
            // the range of the pinch, as scales of the current level
            scroller.minimumZoomScale = pow(2, canvas.range.lowerBound - canvas.level[0])
            scroller.maximumZoomScale = pow(2, canvas.range.upperBound - canvas.level[0])
            // stand where the server says, when that is allowed
            follow(scroller)
            // and place the tiles on the screen
            place(scroller)
        }

        /// The scroll view knows its size: stand where the server says the first time there is a
        /// screen to stand on, and place the tiles on it
        func laidOut(_ scroller: UIScrollView) {
            // nothing to do unless the size changed
            guard scroller.bounds.size != laid else {
                return
            }
            // the first time, the view goes where the server has it; after that, the pixel at
            // the center of the screen stays there
            let old = laid
            laid = scroller.bounds.size
            UIView.performWithoutAnimation {
                if old == .zero {
                    follow(scroller)
                } else {
                    scroller.contentOffset = clamp(
                        CGPoint(
                            x: scroller.contentOffset.x - (laid.width - old.width) / 2,
                            y: scroller.contentOffset.y - (laid.height - old.height) / 2),
                        in: scroller)
                }
                place(scroller)
            }
        }

        /// Lay {content} out at the level of {canvas}, keeping the pixel at the center in place,
        /// with the tiles going straight to their places even when the change is animated
        private func relevel(_ scroller: UIScrollView, to canvas: Canvas) {
            UIView.performWithoutAnimation {
                relayout(scroller, to: canvas)
            }
        }

        /// Lay {content} out at the level of {canvas}, keeping the pixel at the center in place
        private func relayout(_ scroller: UIScrollView, to canvas: Canvas) {
            // the center of the screen, in points of the content as it is laid out now
            let middle = CGPoint(
                x: scroller.bounds.midX / scroller.zoomScale,
                y: scroller.bounds.midY / scroller.zoomScale)
            // and as the pixel of the dataset that is there
            let old = applied ?? canvas.level
            let row = middle.y / pow(2, old[0])
            let col = middle.x / pow(2, old[1])
            // the views of the old level move underneath, resized to where their pixels go at
            // the new one; the tiles the new level shares with the old are taken back when placed
            let grow = (x: pow(2, canvas.level[1] - old[1]), y: pow(2, canvas.level[0] - old[0]))
            for (tile, view) in views {
                let frame = view.frame
                view.frame = CGRect(
                    x: frame.minX * grow.x, y: frame.minY * grow.y,
                    width: frame.width * grow.x, height: frame.height * grow.y)
                retire(tile, view)
            }
            // and so do the ones already retiring, which are older still
            for (tile, view) in retiring where views[tile] == nil {
                let frame = view.frame
                view.frame = CGRect(
                    x: frame.minX * grow.x, y: frame.minY * grow.y,
                    width: frame.width * grow.x, height: frame.height * grow.y)
            }
            views.removeAll()
            // put the scale back to one and lay the content out at the new level
            scroller.zoomScale = 1
            content.frame = CGRect(origin: .zero, size: canvas.layout.size)
            scroller.contentSize = canvas.layout.size
            applied = canvas.level
            // and bring the same pixel back to the center
            scroller.contentOffset = clamp(
                CGPoint(
                    x: col * pow(2, canvas.level[1]) - scroller.bounds.width / 2,
                    y: row * pow(2, canvas.level[0]) - scroller.bounds.height / 2),
                in: scroller)
        }

        /// Place a view for every tile on the screen, with its image once it is at hand; the views
        /// of the tiles that left, whether off the screen or replaced by a rendering of the same
        /// part of the dataset, stay underneath until what took their place has arrived
        private func place(_ scroller: UIScrollView) {
            guard let canvas, applied == canvas.level else {
                return
            }
            // the tiles on the screen, or nearly
            let shown = canvas.layout.placements(in: visible(scroller), margin: canvas.margin)
            let wanted = Set(shown.map(\.tile))
            // the views of the tiles that left retire
            for (tile, view) in views where !wanted.contains(tile) {
                views[tile] = nil
                retire(tile, view)
            }
            // place each tile, reusing its view if it has one, here or among the retiring, and
            // straight where it goes, even when the change is animated
            UIView.performWithoutAnimation {
                for placement in shown {
                    let view = views[placement.tile] ?? reclaim(placement.tile) ?? makeView(for: placement.tile)
                    view.frame = placement.frame
                    view.image = canvas.images[placement.tile]
                }
            }
            // once every tile on the screen has its image, the retiring views have nothing left
            // to cover
            if shown.allSatisfy({ canvas.images[$0.tile] != nil }) {
                retiring.values.forEach { $0.removeFromSuperview() }
                retiring.removeAll()
            }
            // and before then, neither does one hidden under a tile that has arrived
            let covers = views.values.filter { $0.image != nil }.map(\.frame)
            for (tile, view) in retiring where covers.contains(where: { $0.contains(view.frame) }) {
                view.removeFromSuperview()
                retiring[tile] = nil
            }
            // ask for the tiles on the screen, when they are not the ones asked for last
            let tiles = shown.map(\.tile)
            if tiles != asked {
                asked = tiles
                Task { @MainActor in
                    canvas.wanted(tiles)
                }
            }
        }

        /// Keep the {view} of {tile} underneath the current tiles, as long as it has something to
        /// show
        private func retire(_ tile: Tile, _ view: UIImageView) {
            // a view without an image covers nothing
            guard view.image != nil else {
                view.removeFromSuperview()
                return
            }
            // otherwise it takes the place of any older view of the same tile
            retiring.removeValue(forKey: tile)?.removeFromSuperview()
            retiring[tile] = view
        }

        /// Take back the retiring view of {tile}, if it has one
        private func reclaim(_ tile: Tile) -> UIImageView? {
            guard let view = retiring.removeValue(forKey: tile) else {
                return nil
            }
            // it belongs to the current level again, so it goes above whatever is retiring
            content.bringSubviewToFront(view)
            views[tile] = view
            return view
        }

        /// Make the view of {tile}; it shows nothing until its image arrives, so whatever is
        /// underneath shows through
        private func makeView(for tile: Tile) -> UIImageView {
            let view = UIImageView()
            view.contentMode = .scaleToFill
            content.addSubview(view)
            views[tile] = view
            return view
        }

        /// The part of the layout on the screen of {scroller}, in points of the layout
        private func visible(_ scroller: UIScrollView) -> CGRect {
            let scale = scroller.zoomScale
            return CGRect(
                x: scroller.contentOffset.x / scale, y: scroller.contentOffset.y / scale,
                width: scroller.bounds.width / scale, height: scroller.bounds.height / scale)
        }

        /// Stand where the server has the center of the view, unless the canvas is busy or is
        /// already there
        private func follow(_ scroller: UIScrollView) {
            // leave the canvas alone while a finger moves it, a pinch zooms it, or a change of
            // its own is on its way, and while there is no screen to stand on
            guard
                let canvas, canvas.follow, applied == canvas.level,
                !scroller.isTracking, !scroller.isDecelerating, !scroller.isZooming,
                scroller.bounds.size != .zero
            else {
                return
            }
            // where the server's center puts the corner of the screen
            let target = clamp(
                CGPoint(
                    x: canvas.center.col * pow(2, canvas.level[1]) - scroller.bounds.width / 2,
                    y: canvas.center.row * pow(2, canvas.level[0]) - scroller.bounds.height / 2),
                in: scroller)
            // go there, unless the canvas is close enough already; a change of level leaves the
            // two a fraction of a point apart
            let offset = scroller.contentOffset
            if hypot(target.x - offset.x, target.y - offset.y) > 2 {
                scroller.contentOffset = target
            }
        }

        /// Keep {point} within the offsets the content of {scroller} allows
        private func clamp(_ point: CGPoint, in scroller: UIScrollView) -> CGPoint {
            let width = max(scroller.contentSize.width - scroller.bounds.width, 0)
            let height = max(scroller.contentSize.height - scroller.bounds.height, 0)
            return CGPoint(x: min(max(point.x, 0), width), y: min(max(point.y, 0), height))
        }

        /// The pixel of the dataset at the center of the screen of {scroller}
        private func middle(of scroller: UIScrollView, level: [Double]) -> (row: Double, col: Double) {
            let scale = scroller.zoomScale
            return (
                row: scroller.bounds.midY / scale / pow(2, level[0]),
                col: scroller.bounds.midX / scale / pow(2, level[1])
            )
        }

        // the scroll view moved: place the tiles now on the screen, and when a finger moved it,
        // report the pixel it brought to the center
        func scrollViewDidScroll(_ scroller: UIScrollView) {
            place(scroller)
            guard
                let canvas, let level = applied,
                scroller.isTracking || scroller.isDecelerating, !scroller.isZooming
            else {
                return
            }
            let center = middle(of: scroller, level: level)
            canvas.moved(center.row, center.col)
        }

        // the scroll view zoomed: place the tiles now on the screen
        func scrollViewDidZoom(_ scroller: UIScrollView) {
            place(scroller)
        }

        // the scroll view zooms the view that holds the tiles
        func viewForZooming(in scroller: UIScrollView) -> UIView? {
            content
        }

        // a pinch ended at {scale}: the zoom level it reached, and the pixel it brought to the
        // center, are the view's new zoom and center
        func scrollViewDidEndZooming(_ scroller: UIScrollView, with view: UIView?, atScale scale: CGFloat) {
            guard let canvas, let level = applied else {
                return
            }
            // where the pinch left the center, at the level the content is laid out at
            let center = middle(of: scroller, level: level)
            // the level the scale amounts to, within the range
            let change = log2(scale)
            let reached = level.map { min(max($0 + change, canvas.range.lowerBound), canvas.range.upperBound) }
            // report both
            canvas.zoomed(reached)
            canvas.moved(center.row, center.col)
        }
    }
}


// end of file
