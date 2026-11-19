// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


/// A named GraphQL mutation, the input it takes, and the shape of the answer it gets back
///
/// Every mutation of qed takes a single input object, which its text declares as {$input}
struct Mutation<Input: Encodable & Sendable, Answer: Decodable & Sendable>: Sendable {
    // the name of the mutation, as its text declares it
    let name: String
    // the text of the mutation
    let text: String
}


// end of file
