// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


/// One event of a server-sent event stream: its name, and the data it carries
struct Frame: Sendable, Equatable {
    // the name of the event; a frame that names none is a plain message
    let event: String
    // its data, with the lines of a frame that carries several joined by newlines
    let data: String
}


// end of file
