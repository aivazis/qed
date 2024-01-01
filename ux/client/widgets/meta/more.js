// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
// hooks
import { useRange } from './useRange'
import { useDetail } from './useDetail'
// locals
import styles from './styles'


// the detail control bar
export const More = () => {
    // get the current detail level
    const { detail, setDetail } = useDetail()
    // and the range
    const { max } = useRange()
    // marker whether extra styling is needed
    const [polish, setPolish] = React.useState(false)

    // initialize my state
    let state = "disabled"
    // and my controls
    let controls = {}
    // if i'm enabled
    if (detail < max) {
        // adjust my state
        state = "enabled"
        // make handler that increases the level of detail
        const more = () => {
            // adjust
            setDetail(old => old + 1)
            // mark
            setPolish(false)
            // and done
            return
        }
        // make a handler that highlights me when the cursor enters my area
        const highlight = () => {
            // mark
            setPolish(true)
            // and done
            return
        }
        // make a handler that removes the highlight
        const reset = () => {
            // mark
            setPolish(false)
            // and done
            return
        }
        // install them
        controls = {
            // my initial state
            ...controls,
            // plus the state dependent behavior
            onClick: more,
            onMouseEnter: highlight,
            onMouseLeave: reset,
        }
    }

    // mix my paint
    const paint = styles.detailControl(state, polish)
    // and render
    return (
        <div style={paint} {...controls}>more</div>
    )
}


// end of file
