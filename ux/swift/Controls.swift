// -*- swift -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import SwiftUI


/// The controls of a view: the channel it shows, its zoom, and the controllers of the rendering
/// of its channel; every change goes to the server, and comes back to every client
struct Controls: View {
    // the view, and its position among the server's views
    let viewport: Store.Viewport
    // the app's copy of the state of the server, which carries the changes
    let store: Store

    // the contents
    var body: some View {
        Form {
            channel
            zoom
            controllers
        }
    }

    /// The channel the view shows, picked among the channels of its dataset
    @ViewBuilder
    private var channel: some View {
        // the channels of the dataset, and the reader that serves it
        let tags = (viewport.view.dataset?.channels ?? []).compactMap { $0?.tag }
        if let reader = viewport.view.reader?.name, !tags.isEmpty {
            Section("Channel") {
                Picker(
                    "Channel",
                    selection: Binding(
                        get: { viewport.view.channel?.tag ?? "" },
                        set: { tag in store.setChannel(viewport: viewport.index, reader: reader, tag: tag) }
                    )
                ) {
                    ForEach(tags, id: \.self) { tag in
                        Text(tag).tag(tag)
                    }
                }
                .pickerStyle(.inline)
                .labelsHidden()
            }
        }
    }

    /// The zoom: one level for both axes when they move together, one for each otherwise, within
    /// the range the web client allows
    @ViewBuilder
    private var zoom: some View {
        let zoom = viewport.view.zoom
        let vertical = zoom?.vertical ?? 0
        let horizontal = zoom?.horizontal ?? 0
        let coupled = zoom?.coupled ?? true
        let range = -Double(viewport.view.depth ?? 0)...4
        Section("Zoom") {
            if coupled {
                Live(label: "Level", value: vertical, range: range) { level in
                    store.slideZoom(viewport: viewport.index, vertical: level, horizontal: level)
                }
            } else {
                Live(label: "Vertical", value: vertical, range: range) { level in
                    store.slideZoom(viewport: viewport.index, vertical: level, horizontal: horizontal)
                }
                Live(label: "Horizontal", value: horizontal, range: range) { level in
                    store.slideZoom(viewport: viewport.index, vertical: vertical, horizontal: level)
                }
            }
            Toggle(
                "Coupled",
                isOn: Binding(
                    get: { coupled },
                    set: { _ in store.toggleCoupled(viewport: viewport.index) }))
            Button("Reset") {
                store.resetZoom(viewport: viewport.index)
            }
        }
    }

    /// A section for each controller of the rendering of the channel, in the order the server
    /// lists them
    @ViewBuilder
    private var controllers: some View {
        let channel = viewport.view.channel?.name
        let all = (viewport.view.channel?.controllers ?? []).compactMap { $0 }
        if let channel {
            ForEach(Array(all.enumerated()), id: \.offset) { _, controller in
                if let slot = controller.slot {
                    ControllerSection(
                        viewport: viewport.index, channel: channel, slot: slot,
                        controller: controller, store: store)
                }
            }
        }
    }
}


/// The controls of one controller: the ends of a range or the single value, within its bounds,
/// whether it follows the data, and a way back to where it started
struct ControllerSection: View {
    // the view, its channel, and the slot of the controller
    let viewport: Int
    let channel: String
    let slot: String
    // the state of the controller
    let controller: StateQuery.Controller
    // the app's copy of the state of the server, which carries the changes
    let store: Store

    // the contents
    var body: some View {
        // the bounds; a controller without sensible ones has nothing to slide
        let low = controller.min ?? 0
        let high = controller.max ?? 1
        let bounds = low...max(high, low + .ulpOfOne)
        // a range has two ends, a value has one
        let isRange = controller.kind == "RangeController"
        Section(slot) {
            if isRange {
                let from = controller.low ?? low
                let to = controller.high ?? high
                Live(label: "Low", value: from, range: bounds) { value in
                    store.setRange(range(low: min(value, to), high: to))
                }
                Live(label: "High", value: to, range: bounds) { value in
                    store.setRange(range(low: from, high: max(value, from)))
                }
            } else {
                Live(label: "Value", value: controller.value ?? low, range: bounds) { value in
                    store.setValue(
                        ViewMutations.SetValue(
                            viewport: viewport, channel: channel, controller: slot,
                            min: low, value: value, max: high))
                }
            }
            Toggle(
                "Follow the data",
                isOn: Binding(
                    get: { controller.auto ?? false },
                    set: { auto in
                        store.setAuto(
                            ViewMutations.SetAuto(
                                viewport: viewport, channel: channel, controller: slot, auto: auto),
                            range: isRange)
                    }))
            Button("Reset") {
                store.reset(
                    ViewMutations.Slot(viewport: viewport, channel: channel, controller: slot),
                    range: isRange)
            }
        }
    }

    /// The change that sets the range to run from {low} to {high}, within its bounds
    private func range(low: Double, high: Double) -> ViewMutations.SetRange {
        ViewMutations.SetRange(
            viewport: viewport, channel: channel, controller: slot,
            min: controller.min ?? 0, low: low, high: high, max: controller.max ?? 1)
    }
}


/// A slider whose value lives on the server: while a finger moves it, it shows where the finger
/// put it and reports every move; once the finger lets go, it keeps showing that until the
/// server's value changes, so it does not jump back while the last move is on its way
struct Live: View {
    // what the slider sets
    let label: String
    // the server's value, and the range it can take
    let value: Double
    let range: ClosedRange<Double>
    // what to do with each new value
    let change: (Double) -> Void

    // the value the finger put there, until the server has its own say
    @State private var held: Double? = nil
    // whether a finger is on the slider
    @State private var editing = false

    // the contents
    var body: some View {
        // the value on display
        let shown = held ?? value
        VStack(alignment: .leading) {
            LabeledContent(label, value: shown, format: .number.precision(.significantDigits(4)))
            Slider(
                value: Binding(
                    get: { shown },
                    set: { value in
                        held = value
                        change(value)
                    }),
                in: range,
                onEditingChanged: { now in editing = now })
        }
        // once the finger is off, a new value from the server takes over
        .onChange(of: value) {
            if !editing {
                held = nil
            }
        }
    }
}


// end of file
