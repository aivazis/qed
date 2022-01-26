// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useIsActive } from './useIsActive'
import { useChannel } from './useChannel'
import { useToggleChannel } from './useToggleChannel'
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Channel = ({ channel }) => {
    // get the activation status of my reader
    const active = useIsActive()
    // get the active channel
    const activeChannel = useChannel()
    // make a toggle
    const toggleChannel = useToggleChannel(channel)
    // park extra state dependent styling here
    const [polish, setPolish] = React.useState(false)

    // initialize my state
    const state = active && activeChannel === channel ? "selected" : "enabled"

    // make a handler that toggles me as the value of my {axis}
    const toggle = () => {
        // toggle me as the value of my {axis}
        toggleChannel()
        // reset the extra polish
        setPolish(false)
        // all done
        return
    }

    // build my controllers
    let behaviors = {
        // select/unselect when clicked
        onClick: toggle,
    }
    // if i'm enabled
    if (state === "enabled") {
        // make a handler that highlights enabled values
        const highlight = (evt) => {
            // stop this event from bubbling up
            evt.stopPropagation()
            // and quash any side effects
            evt.preventDefault()
            // highlight
            setPolish(true)
            // all done
            return
        }
        // and one that puts everything back
        const reset = (evt) => {
            // stop this event from bubbling up
            evt.stopPropagation()
            // and quash any side effects
            evt.preventDefault()
            // reset the extra polish
            setPolish(false)
            // all done
            return
        }
        // form my controls
        behaviors = {
            // by adding to the default ones
            ...behaviors,
            // the highlighter, when the cursor hovers
            onMouseEnter: highlight,
            // and a reset for when it leaves my client area
            onMouseLeave: reset,
        }
    }

    // mix my paint
    const paint = styles.channel(state, polish)
    // and render
    return (
        <div style={paint} {...behaviors} >
            {channel}
        </div>
    )
}


// end of file
