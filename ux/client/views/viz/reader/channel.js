// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useIsActive } from './useIsActive'
import { useChannel } from './useChannel'
import { useChannelSet } from './useChannelSet'
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Channel = ({ channel }) => {
    // get the activation status of my reader
    const activeReader = useIsActive()
    // get the active channel
    const activeChannel = useChannel()
    // make a toggle
    const channelSet = useChannelSet(channel)
    // park extra state dependent styling here
    const [polish, setPolish] = React.useState(false)

    // initialize my state
    const state = activeReader && (activeChannel?.tag === channel.tag) ? "selected" : "enabled"

    // initialize my controllers
    let behaviors = {}

    // if i'm enabled
    if (state === "enabled") {
        // make a handler that toggles me as the value of my {axis}
        const toggle = () => {
            // toggle me as the value of my {axis}
            channelSet()
            // reset the extra polish
            setPolish(false)
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

        // make a handler that highlights enabled values
        const highlight = () => {
            // highlight
            setPolish(true)
            // all done
            return
        }
        // form my controls
        behaviors = {
            // by adding to the default ones
            ...behaviors,
            // select/unselect when clicked
            onClick: toggle,
            // and a reset for when it leaves my client area
            onMouseLeave: reset,
            // the highlighter, when the cursor hovers
            onMouseEnter: highlight,
        }
    }

    // mix my paint
    const paint = styles.channel(state, polish)
    // and render
    return (
        <div style={paint} {...behaviors} >
            {channel.tag}
        </div>
    )
}


// end of file
