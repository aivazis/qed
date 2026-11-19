// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


/// The changes the app makes to a view of the server, named as the web client names them
enum ViewMutations {
    // move the center of a view to a pixel of its dataset
    static let lookAt = Mutation<LookAt, LookAtAnswer>(
        name: "useLookAtMutation",
        text: """
            mutation useLookAtMutation($input: ViewLookAtInput!) {
                viewLookAt(input: $input) {
                    center { dirty row col }
                }
            }
            """)

    // set the zoom level of a view along each axis
    static let setZoom = Mutation<SetZoom, SetZoomAnswer>(
        name: "useSetLevelZoomMutation",
        text: """
            mutation useSetLevelZoomMutation($input: ViewZoomSetLevelInput!) {
                viewZoomSetLevel(input: $input) {
                    zooms { dirty horizontal vertical }
                }
            }
            """)

    /// The input of a move: the view, and the pixel of its dataset to put at its center
    struct LookAt: Encodable, Sendable, Equatable {
        let viewport: Int
        let row: Double
        let col: Double
    }

    /// The answer to a move
    struct LookAtAnswer: Decodable, Sendable {
        let viewLookAt: Moved?
    }

    /// The center of the view after the move
    struct Moved: Decodable, Sendable {
        let center: StateQuery.Center?
    }

    /// The input of a zoom: the view, and its level along each axis
    struct SetZoom: Encodable, Sendable, Equatable {
        let viewport: Int
        let vertical: Double
        let horizontal: Double
    }

    /// The answer to a zoom
    struct SetZoomAnswer: Decodable, Sendable {
        let viewZoomSetLevel: Zoomed?
    }

    /// The zoom of every view the change reached, since views can be zoomed together
    struct Zoomed: Decodable, Sendable {
        let zooms: [StateQuery.Zoom?]?
    }
}


// end of file
