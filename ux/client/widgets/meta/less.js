// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
// hooks
import { useRange } from './useRange'
import { useDetail } from './useDetail'
// locals
import styles from './styles'


// the detail control bar
export const Less = () => {
    // get the current detail level
    const { detail, setDetail } = useDetail()
    // and the range
    const { min } = useRange()
    // marker whether extra styling is needed
    const [polish, setPolish] = React.useState(false)

    // initialize my state
    let state = "disabled"
    // and my controls
    let controls = {}
    // if i'm enabled
    if (detail > min) {
        // adjust my state
        state = "enabled"
        // make handler that reduces the level of detail
        const less = () => {
            // adjust
            setDetail(old => old - 1)
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
            onClick: less,
            onMouseEnter: highlight,
            onMouseLeave: reset,
        }
    }

    // mix my paint
    const paint = styles.detailControl(state, polish)
    // and render
    return (
        <div style={paint} {...controls}>less</div>
    )
}


// end of file
