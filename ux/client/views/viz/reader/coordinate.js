// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useReader } from './useReader'
import { useIsActive } from './useIsActive'
import { useSelections } from './useSelections'
import { useAvailableSelectors } from './useAvailableSelectors'
import { useToggleCoordinate } from './useToggleCoordinate'
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Coordinate = ({ axis, coordinate }) => {
    // get the reader
    const reader = useReader()
    // get the selection status of my reader
    const activeReader = useIsActive()
    // ask for the pile of possible values for my {axis}
    const available = useAvailableSelectors(axis)
    // make a toggle
    const toggleCoordinate = useToggleCoordinate(axis, coordinate)
    // park extra state dependent styling here
    const [polish, setPolish] = React.useState(false)
    // get the current selections; this applies only to the active reader, so careful not to pollute
    // the logic with stuff that doesn't belong to me
    const selections = useSelections()

    // i'm a possible solution if and only if the set of {available} values contains my {coordinate}
    const possible = available.has(coordinate)

    // figure out my state; first the easy part: am i a plausible selection?
    let state = possible ? "enabled" : "disabled"
    // if i am part of the active reader
    if (activeReader) {
        // get the current value of my axis
        const currentCoordinate = selections.get(axis)
        // and i am the current selection for my axis
        if (currentCoordinate == coordinate) {
            // upgrade me
            state = "selected"
        }
        // otherwise, check whether i'm viable
        else if (possible) {
            // let's reset: assume i'm not a viable solution to the current selection
            state = "disabled"
            // now, go through all datasets
            for (const dataset of reader.datasets) {
                // clone the {selections}
                // N.B.: don't factor this out of the loop: we destroy it, so we need a new one
                //       on every iteration
                const candidate = new Map(selections)
                // set me as the value of {axis}, making a part of the solution
                candidate.set(axis, coordinate)
                // go though the selections of the {dataset}
                for (const { name, value } of dataset.selector) {
                    // if the {value} for {name} matches what my {candidate} has
                    if (candidate.get(name) === value) {
                        // remove it
                        candidate.delete(name)
                    }
                }
                // if the candidate is now empty
                if (candidate.size === 0) {
                    // the dataset selector matched everything in the candidate, so...
                    state = "enabled"
                    // and look no further
                    break
                }
            }
        }
    }

    // make a handler that toggles me as the value of my {axis}
    const toggle = evt => {
        // stop this event from propagating
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // if there are multiple possible solutions
        if (available.size > 1) {
            // toggle me as the value of my {axis}
            toggleCoordinate()
            // reset the extra polish
            setPolish(false)
        }
        // all done
        return
    }
    // and one that removes any extra polish
    const reset = () => {
        // reset the extra polish
        setPolish(false)
        // all done
        return
    }

    // build my controllers
    let behaviors = {
        onMouseLeave: reset,
    }
    // if i'm enabled
    if (state === "enabled") {
        // make a handler that highlights enabled values
        const highlight = () => {
            // highlight
            setPolish(true)
            // all done
            return
        }
        // assemble the behaviors
        behaviors = {
            // by extending what was already there
            ...behaviors,
            // with the coordinate toggle
            onClick: toggle,
            // and the highlighter
            onMouseEnter: highlight,
        }
    }
    // if i'm selected
    else if (state == "selected") {
        // assemble the behaviors
        behaviors = {
            // by extending what was already there
            ...behaviors,
            // with the coordinate toggle only; the coordinate is already highlighted
            onClick: toggle,
        }
    }

    // mix my paint
    const paint = styles.coordinate(state, polish)
    // pick my tip
    const tip = (
        state === "disabled"
            ? `the ${coordinate} ${axis} is not available in '${reader.name}'`
            : `select the ${coordinate} ${axis} of '${reader.name}'`
    )

    // and render
    return (
        <div style={paint} {...behaviors} title={tip}>
            {coordinate}
        </div>
    )
}


// end of file
