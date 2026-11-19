// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import CoreGraphics
import Foundation
import Testing


/// The address of a tile is the one the web client builds, and the server serves
@Test func spellsTheAddressOfATile() {
    // a tile of the GCOV view on the development server, two levels out
    let tile = Tile(
        api: "data", viewport: 0, dataset: "gcov-033_166_D_069-P05023.L.A.HHHH",
        channel: "covarianceMasked", session: "5f94", level: [2, 2],
        origin: [1024, 1024], shape: [512, 512])
    // has the path the server reads, and carries its session as a parameter
    #expect(tile.path == "data/0/gcov-033_166_D_069-P05023.L.A.HHHH/covarianceMasked/2x2/1024x1024+512x512")
    #expect(tile.query == [URLQueryItem(name: "session", value: "5f94")])
}

/// At a whole level below zero, the server does all the zooming and tiles keep their size
@Test func splitsAWholeLevel() {
    // an axis of the GCOV dataset, two levels out
    let axis = TileLayout.axis(extent: 17280, origin: 0, tile: 512, level: -2)
    // is rendered reduced four times, as eight whole tiles and what is left
    #expect(axis.magnification == 2)
    #expect(axis.segments.count == 9)
    #expect(axis.segments.last == TileLayout.Segment(origin: 4096, extent: 224, start: 4096, length: 224))
    // and is as long on the screen as the reduced dataset
    #expect(axis.length == 4320)
}

/// The fraction of a level is the app's: tiles are resized by it
@Test func resizesTilesByTheFraction() {
    // the same axis two and a half levels out
    let axis = TileLayout.axis(extent: 17280, origin: 0, tile: 512, level: -2.5)
    // is still rendered two levels out
    #expect(axis.magnification == 2)
    // but shown smaller by a further half level
    let shrink = pow(2.0, -0.5)
    #expect(abs(axis.segments[1].start - 512 * shrink) < 1e-9)
    #expect(abs(axis.length - 4320 * shrink) < 1e-9)
}

/// A level above zero is all the app's: the server renders at full size and the app enlarges
@Test func enlargesAboveLevelZero() {
    // an axis half a level in
    let axis = TileLayout.axis(extent: 1000, origin: 0, tile: 512, level: 0.5)
    // is rendered at full size
    #expect(axis.magnification == 0)
    #expect(axis.segments.map(\.extent) == [512, 488])
    // and enlarged on the screen
    #expect(abs(axis.length - 1000 * pow(2.0, 0.5)) < 1e-9)
}

/// The origin of the dataset shifts the tiles the server is asked for, not where they go
@Test func shiftsTilesByTheOrigin() {
    // an axis that starts at pixel 100
    let axis = TileLayout.axis(extent: 1024, origin: 100, tile: 512, level: 0)
    // asks for tiles from there
    #expect(axis.segments.map(\.origin) == [100, 612])
    // and draws them from the corner of the screen
    #expect(axis.segments.map(\.start) == [0, 512])
}

/// The layout covers the dataset with tiles that meet edge to edge
@Test func coversTheDataset() {
    // the GCOV view, two levels out
    let layout = TileLayout(
        api: "data", viewport: 0, dataset: "d", channel: "c", session: "s",
        shape: [17280, 17496], origin: [0, 0], tile: [512, 512], level: [-2, -2])
    // is as large as the reduced dataset
    #expect(layout.size == CGSize(width: 4374, height: 4320))
    // and is covered by a tile for every pair of runs
    #expect(layout.placements.count == 9 * 9)
    // whose areas add up to the whole
    let area = layout.placements.reduce(0) { $0 + $1.frame.width * $1.frame.height }
    #expect(area == layout.size.width * layout.size.height)
}

/// Only the tiles on the screen, or near it, are wanted
@Test func picksTheTilesOnTheScreen() {
    // a layout of four by four tiles
    let layout = TileLayout(
        api: "data", viewport: 0, dataset: "d", channel: "c", session: "s",
        shape: [2048, 2048], origin: [0, 0], tile: [512, 512], level: [0, 0])
    // a screen inside the first tile wants only that one
    let one = layout.placements(in: CGRect(x: 100, y: 100, width: 200, height: 200), margin: 0)
    #expect(one.map(\.tile.origin) == [[0, 0]])
    // and a margin that reaches into the neighbors wants them too
    let more = layout.placements(in: CGRect(x: 100, y: 100, width: 200, height: 200), margin: 300)
    #expect(more.count == 4)
}

/// A mutation travels with its input under the name every mutation of qed gives it
@Test func encodesTheInputOfAMutation() throws {
    // a move of the first view
    let input = ViewMutations.LookAt(viewport: 0, row: 7450, col: 9070)
    // spelled out as a request
    let body = try Client.encode(ViewMutations.lookAt, input: input)
    let request = try #require(try JSONSerialization.jsonObject(with: body) as? [String: Any])
    // names the mutation, and carries the input as the variable {input}
    #expect(request["operationName"] as? String == "useLookAtMutation")
    let variables = try #require(request["variables"] as? [String: Any])
    let carried = try #require(variables["input"] as? [String: Any])
    #expect(carried["viewport"] as? Int == 0)
    #expect(carried["row"] as? Double == 7450)
    #expect(carried["col"] as? Double == 9070)
}


// end of file
