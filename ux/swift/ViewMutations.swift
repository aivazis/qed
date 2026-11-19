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

    // let the zoom of a view move along both axes together, or each on its own
    static let toggleCoupled = Mutation<Viewport, Acknowledged>(
        name: "useToggleCoupledZoomMutation",
        text: """
            mutation useToggleCoupledZoomMutation($input: ViewZoomToggleCoupledInput!) {
                viewZoomToggleCoupled(input: $input) { __typename }
            }
            """)

    // put the zoom of a view back where it started
    static let resetZoom = Mutation<Viewport, Acknowledged>(
        name: "useResetZoomMutation",
        text: """
            mutation useResetZoomMutation($input: ViewZoomResetInput!) {
                viewZoomReset(input: $input) { __typename }
            }
            """)

    // show another channel of the dataset in a view
    static let setChannel = Mutation<SetChannel, Acknowledged>(
        name: "useChannelSetMutation",
        text: """
            mutation useChannelSetMutation($input: ViewChannelSetInput!) {
                viewChannelSet(input: $input) { __typename }
            }
            """)

    // set the ends of a range controller, and its bounds
    static let setRange = Mutation<SetRange, Acknowledged>(
        name: "useUpdateRangeControllerMutation",
        text: """
            mutation useUpdateRangeControllerMutation($input: ViewRangeUpdateInput!) {
                viewRangeUpdate(input: $input) { __typename }
            }
            """)

    // set the value of a value controller, and its bounds
    static let setValue = Mutation<SetValue, Acknowledged>(
        name: "useUpdateValueControllerMutation",
        text: """
            mutation useUpdateValueControllerMutation($input: ViewValueUpdateInput!) {
                viewValueUpdate(input: $input) { __typename }
            }
            """)

    // let a range controller follow the data, or hold it where it is
    static let setRangeAuto = Mutation<SetAuto, Acknowledged>(
        name: "useAutoRangeControllerMutation",
        text: """
            mutation useAutoRangeControllerMutation($input: ViewRangeAutoSetInput!) {
                viewRangeAutoSet(input: $input) { __typename }
            }
            """)

    // let a value controller follow the data, or hold it where it is
    static let setValueAuto = Mutation<SetAuto, Acknowledged>(
        name: "useAutoValueControllerMutation",
        text: """
            mutation useAutoValueControllerMutation($input: ViewValueAutoSetInput!) {
                viewValueAutoSet(input: $input) { __typename }
            }
            """)

    // put a range controller back where it started
    static let resetRange = Mutation<Slot, Acknowledged>(
        name: "useResetRangeControllerMutation",
        text: """
            mutation useResetRangeControllerMutation($input: ViewRangeResetInput!) {
                viewRangeReset(input: $input) { __typename }
            }
            """)

    // put a value controller back where it started
    static let resetValue = Mutation<Slot, Acknowledged>(
        name: "useResetValueControllerMutation",
        text: """
            mutation useResetValueControllerMutation($input: ViewValueResetInput!) {
                viewValueReset(input: $input) { __typename }
            }
            """)

    /// The input of a change that names nothing but the view
    struct Viewport: Encodable, Sendable, Equatable {
        let viewport: Int
    }

    /// The input of a change of channel: the view, its reader, and the tag of the channel
    struct SetChannel: Encodable, Sendable, Equatable {
        let viewport: Int
        let reader: String
        let value: String
    }

    /// The input of a change of a range: the view, its channel, the slot of the controller, and
    /// the ends of the range within its bounds
    struct SetRange: Encodable, Sendable, Equatable {
        let viewport: Int
        let channel: String
        let controller: String
        let min: Double
        let low: Double
        let high: Double
        let max: Double
    }

    /// The input of a change of a value: the view, its channel, the slot of the controller, and
    /// the value within its bounds
    struct SetValue: Encodable, Sendable, Equatable {
        let viewport: Int
        let channel: String
        let controller: String
        let min: Double
        let value: Double
        let max: Double
    }

    /// The input that lets a controller follow the data, or holds it
    struct SetAuto: Encodable, Sendable, Equatable {
        let viewport: Int
        let channel: String
        let controller: String
        let auto: Bool
    }

    /// The input that names a controller: the view, its channel, and the slot
    struct Slot: Encodable, Sendable, Equatable {
        let viewport: Int
        let channel: String
        let controller: String
    }

    /// An answer the app does not read, since the change comes back through the stream
    struct Acknowledged: Decodable, Sendable {}

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
