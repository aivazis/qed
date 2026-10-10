// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Meta } from '~/widgets'

// locals
// hooks
import { useEngine } from './useEngine'
import { useEngineSet } from './useEngineSet'
// styles
import styles from './styles'


// the engines that can draw the tiles of a view, by the value the server knows and the label shown
const engines = [
    { value: "iterators", label: "iter" },
    { value: "flow", label: "flow" },
]


// pick the engine that draws the tiles of the active view: the fused iterators, or the pipeline of
// its channel's recipe, which is grayed out when it cannot draw this dataset
export const Engine = () => {
    // the engine that draws the tiles now, and whether the pipeline can
    const { engine, flowable } = useEngine()
    // without a channel on display there are no tiles to draw
    if (!engine) {
        // so there is nothing to pick
        return null
    }
    // render; the engines form a radiogroup, the client's identity for this control
    return (
        <Meta.Entry attribute="engine" style={styles.channels()}>
            <div role="radiogroup" aria-label="engine" data-qed-control="engine">
                {engines.map(({ value, label }) => (
                    <Option key={value} value={value} label={label}
                        current={engine} available={value === "iterators" || flowable} />
                ))}
            </div>
        </Meta.Entry>
    )
}


// one of the engines
const Option = ({ value, label, current, available }) => {
    // make the handler that picks an engine
    const set = useEngineSet()
    // park extra state dependent styling here
    const [polish, setPolish] = React.useState(false)
    // my state: the one drawing the tiles, one that can be picked, or one that cannot
    const state = value === current ? "selected" : available ? "enabled" : "disabled"

    // initialize my controllers
    let behaviors = {}
    // if i can be picked
    if (state === "enabled") {
        // form my controls
        behaviors = {
            // pick me when clicked
            onClick: () => {
                // pick me
                set(value)
                // reset the extra polish
                setPolish(false)
                // all done
                return
            },
            // highlight me when the cursor hovers
            onMouseEnter: () => setPolish(true),
            // and stop when it leaves
            onMouseLeave: () => setPolish(false),
        }
    }

    // mix my paint
    const paint = styles.engine(state, polish)
    // and render; ARIA carries the selected and disabled states
    return (
        <div
            style={paint}
            role="radio"
            aria-checked={state === "selected"}
            aria-disabled={state === "disabled"}
            data-qed-value={value}
            {...behaviors} >
            {label}
        </div>
    )
}


// end of file
