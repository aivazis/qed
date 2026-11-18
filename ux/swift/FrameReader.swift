// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


/// Cut the bytes of a server-sent event stream into frames, as they arrive
///
/// A frame is a run of lines that ends with an empty one. Each line is a field, {name: value},
/// or a comment, which starts with a colon and carries nothing for the app
struct FrameReader {
    // the bytes of the line in progress
    private var line: [UInt8] = []
    // the name of the frame in progress, once a line has named it
    private var event: String? = nil
    // the data lines of the frame in progress
    private var data: [String] = []

    /// Take in the next {byte} of the stream, and hand back the frame it completes, if any
    mutating func consume(_ byte: UInt8) -> Frame? {
        // anything other than the end of a line belongs to the line in progress
        guard byte == newline else {
            line.append(byte)
            return nil
        }
        // the line is complete; read it, without the carriage return that may precede the newline
        let text = String(decoding: line.last == carriage ? line.dropLast() : line[...], as: UTF8.self)
        // and start the next one
        line.removeAll(keepingCapacity: true)
        // an empty line completes the frame in progress
        if text.isEmpty {
            return complete()
        }
        // everything else adds to it
        absorb(text)
        // and completes nothing
        return nil
    }

    /// Fold the field on the line {text} into the frame in progress
    private mutating func absorb(_ text: String) {
        // a comment carries nothing; the server sends them to keep the connection busy
        if text.hasPrefix(":") {
            return
        }
        // split the line into the name of the field and its value; a line without a colon is a
        // field with an empty value
        let colon = text.firstIndex(of: ":") ?? text.endIndex
        let name = String(text[..<colon])
        var value = colon < text.endIndex ? text[text.index(after: colon)...] : ""
        // a single space after the colon is part of the format, not of the value
        if value.hasPrefix(" ") {
            value = value.dropFirst()
        }
        // record the fields that matter to the app; the rest are left alone
        switch name {
        case "event":
            event = String(value)
        case "data":
            data.append(String(value))
        default:
            break
        }
        // all done
        return
    }

    /// Hand back the frame in progress, if it carries anything, and start a new one
    private mutating func complete() -> Frame? {
        // whatever this frame turns out to be, the next one starts empty
        defer {
            event = nil
            data.removeAll()
        }
        // a frame with neither a name nor data is not an event
        if event == nil && data.isEmpty {
            return nil
        }
        // assemble it; a frame without a name is a plain message
        return Frame(event: event ?? "message", data: data.joined(separator: "\n"))
    }

    // the bytes that end a line
    private let newline = UInt8(ascii: "\n")
    private let carriage = UInt8(ascii: "\r")
}


// end of file
