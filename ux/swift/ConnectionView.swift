// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import SwiftUI


/// Show the link to a qed server, what its stream has said, and the views it holds; the view
/// picked here is the one the iPad shows
struct ConnectionView: View {
    // the stream whose state this shows
    let stream: EventStream
    // the app's copy of the state of the server
    let store: Store
    // the position of the view the iPad shows
    @Binding var active: Int

    // the contents
    var body: some View {
        Form {
            // the server and the state of its link
            Section("Server") {
                LabeledContent("Address", value: stream.server.base.absoluteString)
                LabeledContent("Link") {
                    HStack(spacing: 6) {
                        Image(systemName: "circle.fill")
                            .imageScale(.small)
                        Text(link.label)
                    }
                    .foregroundStyle(link.color)
                }
            }
            // what the stream has said
            Section("Stream") {
                LabeledContent("Instance", value: stream.instance ?? "unknown")
                    .monospaced()
                LabeledContent("Changes", value: stream.changes, format: .number)
            }
            // the views of the server, and why they may be out of date; a tap picks one
            Section("Views") {
                if let problem = store.problem {
                    Text(problem)
                        .foregroundStyle(.red)
                }
                ForEach(store.views, id: \.index) { viewport in
                    Button {
                        active = viewport.index
                    } label: {
                        ViewSummary(view: viewport.view, picked: viewport.index == active)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .navigationTitle("qed")
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


/// Summarize one view of the server: what it shows, how large it is, and at what zoom
struct ViewSummary: View {
    // the view
    let view: StateQuery.View
    // whether it is the one the iPad shows
    let picked: Bool

    // the contents
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            // the view by name, marked when it is the one on the screen
            Label(view.name, systemImage: picked ? "eye.fill" : "eye.slash")
                .font(.headline)
                .foregroundStyle(picked ? Color.accentColor : Color.primary)
            // what it shows: the reader, the value picked for each of its selectors, in the order
            // the server lists them
            LabeledContent("Reader", value: view.reader?.name ?? "none")
            ForEach(Array(selections.enumerated()), id: \.offset) { _, selection in
                LabeledContent(selection.name, value: selection.value)
            }
            LabeledContent("Channel", value: view.channel?.tag ?? "none")
            LabeledContent("Shape", value: shape)
            LabeledContent("Zoom", value: zoom)
        }
    }

    // the selectors of the reader and the values the view picked, skipping any the server left
    // unnamed; a selector without a value shows as a question mark
    private var selections: [(name: String, value: String)] {
        (view.selections ?? []).compactMap { selection in
            guard let name = selection?.name else {
                return nil
            }
            return (name, selection?.value ?? "?")
        }
    }

    // the shape of the dataset, row first, as the server reports it
    private var shape: String {
        // a view without a dataset has no shape
        guard let extents = view.dataset?.shape else {
            return "none"
        }
        // a missing extent shows as a question mark
        return extents.map { $0.map(String.init) ?? "?" }.joined(separator: " × ")
    }

    // the zoom level along each axis, vertical first, and whether the two move together
    private var zoom: String {
        // a view without a zoom has none to show
        guard let zoom = view.zoom else {
            return "none"
        }
        // a missing level shows as a question mark
        let level = { (value: Double?) in value.map { String(format: "%g", $0) } ?? "?" }
        // assemble
        let pair = "(\(level(zoom.vertical)), \(level(zoom.horizontal)))"
        return zoom.coupled == true ? "\(pair), coupled" : pair
    }
}


// end of file
