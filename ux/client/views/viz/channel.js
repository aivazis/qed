// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useChannelInView } from './useChannelInView'
import { useVisualizeChannel } from './useVisualizeChannel'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Channel = ({ reader, dataset, channel, behaviors }) => {
    // local state for the state dependent paint
    const [polish, setPolish] = React.useState(null)
    // access to the active view
    const getChannelInView = useChannelInView()
    // handler that places a channel in a view
    const visualizeChannel = useVisualizeChannel()
    // unpack the active view spec
    const {
        dataset: { uuid: activeDataset = null } = {},
        channel: activeChannel = null
    } = getChannelInView()

    // am i the active channel
    const amActive = (activeDataset === dataset.uuid && activeChannel === channel)
    // deduce my state
    const state = amActive ? "active" : "enabled"

    // get the channel style
    const channelStyle = styles.channel
    // mix the styles
    const boxStyle = styles.channel.box
    const nameStyle = {
        // basics from the local style
        ...channelStyle.name.base,
        // the state dependent style, if any
        ...channelStyle.name[state],
        // and the transient style that takes care of highlighting
        ...polish,
    }

    // make a pile of event handlers
    let controls = {}
    // when a channel is enabled
    if (state === "enabled") {
        // make a handler for highlighting a channel
        const highlight = () => {
            // mix the highlight style and apply it
            setPolish(channelStyle.name.available)
            // all done
            return
        }

        // and one for removing the highlight
        const reset = () => {
            // reset my polish
            setPolish(null)
            // all done
            return
        }

        const select = () => {
            // reset my polish
            setPolish(null)
            // assemble the channel spec
            const spec = { reader, dataset, channel }
            // and adjust the contents of the active view
            visualizeChannel(spec)
            // all done
            return
        }

        // gather all the handlers in a single object
        controls = {
            // selection
            onClick: select,
            // styling
            onMouseEnter: highlight,
            onMouseLeave: reset,
        }
    }
    // in any case, mix in the whatever the client supplied
    controls = { ...controls, ...behaviors }

    // render
    return (
        <div style={boxStyle}>
            <div style={nameStyle} {...controls} >
                {channel}
            </div>
        </div>
    )
}


// end of file