// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useReader } from './useReader'
import { useDataset } from './useDataset'
import { useChannel } from './useChannel'
import { useToggleChannel } from './useToggleChannel'
import { useGetView } from '../viz/useGetView'
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Channel = ({ channel }) => {
    // get the active view
    const view = useGetView()
    // the current reader
    const reader = useReader()
    // the current dataset
    const dataset = useDataset()
    // and the current channel
    const current = useChannel()
    // make a toggle
    const toggleChannel = useToggleChannel(channel)
    // park extra state dependent styling here
    const [polish, setPolish] = React.useState(null)

    // i'm selected when my info matches the active view and i'm the current channel
    const selected = (
        view?.reader?.uuid === reader.uuid &&
        view?.dataset?.uuid == dataset.uuid &&
        view?.channel === channel
    )
    // initialize my state
    const state = selected ? "selected" : "enabled"

    // make a handler that toggles me as the value of my {axis}
    const toggle = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // toggle me as the value of my {axis}
        toggleChannel()
        // all done
        return
    }
    // make a handler that highlights enabled values
    const highlight = (evt) => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // if i am available
        if (state === "enabled") {
            // highlight
            setPolish(styles.channel("available"))
        }
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
        setPolish(null)
        // all done
        return
    }

    // build my controllers
    const behaviors = {
        // select/unselect when clicked
        onClick: toggle,
        // when the cursor hovers
        onMouseEnter: highlight,
        // and when it leaves
        onMouseLeave: reset,
    }

    // mix my paint
    const paint = { ...styles.channel(state), ...polish }
    // and render
    return (
        <div style={paint} {...behaviors} >
            {channel}
        </div>
    )
}


// end of file
