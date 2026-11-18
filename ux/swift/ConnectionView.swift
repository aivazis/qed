// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import SwiftUI


/// Show the link to a qed server: where it is, whether its stream flows, which run of the server
/// is on the other end, and how many changes it has announced
struct ConnectionView: View {
    // the stream whose state this shows
    let stream: EventStream

    // the contents
    var body: some View {
        NavigationStack {
            Form {
                // the server and the state of its link
                Section("Server") {
                    LabeledContent("Address", value: stream.server.base.absoluteString)
                    LabeledContent("Link") {
                        Label(link.label, systemImage: "circle.fill")
                            .foregroundStyle(link.color)
                    }
                }
                // what the stream has said
                Section("Stream") {
                    LabeledContent("Instance", value: stream.instance ?? "unknown")
                        .monospaced()
                    LabeledContent("Changes", value: stream.changes, format: .number)
                }
            }
            .navigationTitle("qed")
        }
    }

    // the words and the color that show the state of the link
    private var link: (label: String, color: Color) {
        switch stream.link {
        case .connecting: return ("connecting", .orange)
        case .open: return ("open", .green)
        case .lost: return ("lost", .red)
        }
    }
}


// end of file
