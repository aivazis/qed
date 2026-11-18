// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


/// A named GraphQL operation, and the shape of the answer it gets from the server
struct Operation<Answer: Decodable & Sendable>: Sendable {
    // the name of the operation, as its text declares it
    let name: String
    // the text of the operation
    let text: String
}


// end of file
