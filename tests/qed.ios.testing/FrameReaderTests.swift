// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import Testing


/// Feed {text} to a fresh reader, one byte at a time, and collect the frames it completes
func frames(in text: String) -> [Frame] {
    // make a reader
    var reader = FrameReader()
    // and a pile for what it hands back
    var frames: [Frame] = []
    // feed it the bytes in order
    for byte in Array(text.utf8) {
        if let frame = reader.consume(byte) {
            frames.append(frame)
        }
    }
    // all done
    return frames
}

/// The greeting that opens every stream is a frame with a name and data
@Test func readsTheGreeting() {
    // the opening of a stream from qed
    let text = "event: hello\ndata: {\"instance\": \"a7ed\"}\n\n"
    // is one named frame
    #expect(frames(in: text) == [Frame(event: "hello", data: "{\"instance\": \"a7ed\"}")])
}

/// A frame that names no event is a plain message
@Test func readsAMessage() {
    // a change, as qed announces it
    let text = "data: {\"type\": \"change\"}\n\n"
    // is one message
    #expect(frames(in: text) == [Frame(event: "message", data: "{\"type\": \"change\"}")])
}

/// Frames that follow each other stay apart, which is what the blank line between them is for
@Test func separatesConsecutiveFrames() {
    // two changes in a row
    let text = "data: one\n\ndata: two\n\n"
    // are two frames
    #expect(frames(in: text) == [
        Frame(event: "message", data: "one"),
        Frame(event: "message", data: "two"),
    ])
}

/// Comments carry nothing, so the keepalives between frames make none
@Test func skipsComments() {
    // keepalives around a change
    let text = ": keepalive\n\ndata: change\n\n: keepalive\n\n"
    // leave only the change
    #expect(frames(in: text) == [Frame(event: "message", data: "change")])
}

/// The data lines of one frame are joined by newlines
@Test func joinsDataLines() {
    // a frame whose data spans two lines
    let text = "data: first\ndata: second\n\n"
    // carries both, one per line
    #expect(frames(in: text) == [Frame(event: "message", data: "first\nsecond")])
}

/// Lines may end with a carriage return before the newline
@Test func acceptsCarriageReturns() {
    // the greeting, with the line endings some servers send
    let text = "event: hello\r\ndata: x\r\n\r\n"
    // reads the same as without them
    #expect(frames(in: text) == [Frame(event: "hello", data: "x")])
}

/// A frame still in progress when the bytes stop is not handed back
@Test func holdsAnIncompleteFrame() {
    // a frame without its closing blank line
    let text = "data: partial\n"
    // completes nothing
    #expect(frames(in: text).isEmpty)
}


// end of file
