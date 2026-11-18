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
                        selections { name value }
                        reader { name }
                        dataset { shape origin channels { tag } }
                        channel { tag }
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

    /// A view: the values it picked for the selectors of its reader, the reader, dataset and
    /// channel it shows, and its zoom
    struct View: Decodable, Sendable {
        let name: String
        let selections: [Selector?]?
        let reader: Reader?
        let dataset: Dataset?
        let channel: Channel?
        let zoom: Zoom?
    }

    /// A selector of the reader of a view, and the value the view picked for it
    struct Selector: Decodable, Sendable {
        let name: String?
        let value: String?
    }

    /// The reader of a view
    struct Reader: Decodable, Sendable {
        let name: String?
    }

    /// The dataset of a view: its shape and origin, row first, and its channels
    struct Dataset: Decodable, Sendable {
        let shape: [Int?]?
        let origin: [Int?]?
        let channels: [Channel?]?
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
