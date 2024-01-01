// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useReader } from './useReader'
import { useIsActive } from './useIsActive'
import { useSelector } from './useSelector'
import { useCandidates } from './useCandidates'
import { useToggleCoordinate } from './useToggleCoordinate'
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Coordinate = ({ axis, coordinate }) => {
    // get the reader
    const reader = useReader()
    // get the selection status of my reader
    const activeReader = useIsActive()
    // and the current selector
    const selector = useSelector()
    // ask for the pile of possible values for my {axis}
    const candidates = useCandidates(axis)
    // make a toggle
    const toggleCoordinate = useToggleCoordinate(axis, coordinate)
    // park extra state dependent styling here
    const [polish, setPolish] = React.useState(false)

    // i'm a possible solution if and only is the set of {candidates} contains my {coordinate}
    const possible = candidates.has(coordinate)
    // get the current value of my axis
    const currentCoordinate = selector.get(axis)

    // figure out my state
    let state = "disabled"
    // if my reader is active and i'm the currently selected value of my {axis}
    if (activeReader && currentCoordinate === coordinate) {
        // mark me as selected
        state = "selected"
    }
    // if i'm not part of the selection solution
    else if (!possible) {
        // mark me as disabled
        state = "disabled"
    }
    // otherwise, check whether i'm viable
    else {
        // go through the datasets
        for (const dataset of reader.datasets) {
            // clone the {selector}
            // N.B.: don't factor this out of the loop: we destroy it, so we need a new one
            //       on every iteration
            const candidate = new Map(selector)
            // set me as the value of {axis}
            candidate.set(axis, coordinate)
            // go though the selector of the {dataset}
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

    // make a handler that toggles me as the value of my {axis}
    const toggle = () => {
        // if there are multiple possible solutions
        if (candidates.size > 1) {
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
    // and render
    return (
        <div style={paint} {...behaviors} >
            {coordinate}
        </div>
    )
}


// end of file
