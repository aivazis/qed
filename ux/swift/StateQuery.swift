// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


/// The state of the server's views: what each one shows, and at what zoom
///
/// The types follow the schema: every field it allows to be missing is optional here too
enum StateQuery {
    // the operation, named as the web client names it
    static let operation = Operation<Answer>(
        name: "qedStateQuery",
        text: """
            query qedStateQuery {
                qed {
                    views {
                        name
                        session
                        depth
                        selections { name value }
                        reader { name api }
                        dataset { name shape origin tile channels { tag } }
                        channel { tag }
                        center { row col }
                        zoom { vertical horizontal coupled }
                    }
                }
            }
            """)

    /// The answer
    struct Answer: Decodable, Sendable {
        let qed: QED?
    }

    /// The server
    struct QED: Decodable, Sendable {
        let views: [View?]?
    }

    /// A view: the session it belongs to, how far it can zoom out, the values it picked for the
    /// selectors of its reader, the reader, dataset and channel it shows, the pixel at its center,
    /// and its zoom
    struct View: Decodable, Sendable {
        let name: String
        let session: String?
        let depth: Int?
        let selections: [Selector?]?
        let reader: Reader?
        let dataset: Dataset?
        let channel: Channel?
        let center: Center?
        let zoom: Zoom?
    }

    /// A selector of the reader of a view, and the value the view picked for it
    struct Selector: Decodable, Sendable {
        let name: String?
        let value: String?
    }

    /// The reader of a view, and the path under which the server serves its tiles
    struct Reader: Decodable, Sendable {
        let name: String?
        let api: String?
    }

    /// The dataset of a view: its name, its shape, origin and tile, row first, and its channels
    struct Dataset: Decodable, Sendable {
        let name: String?
        let shape: [Int?]?
        let origin: [Int?]?
        let tile: [Int?]?
        let channels: [Channel?]?
    }

    /// The pixel of the dataset at the center of a view
    struct Center: Decodable, Sendable {
        let row: Double?
        let col: Double?
    }

    /// A channel of a dataset
    struct Channel: Decodable, Sendable {
        let tag: String?
    }

    /// The zoom of a view: a level along each axis, and whether the two move together
    struct Zoom: Decodable, Sendable {
        let vertical: Double?
        let horizontal: Double?
        let coupled: Bool?
    }
}


// end of file
