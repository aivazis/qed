// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Context } from './context'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Channel = ({ reader, dataset, channel, state = "enabled", behaviors }) => {
    // local state for the state dependent paint
    const [polish, setPolish] = React.useState(null)
    // access to the active view
    const { viewChannel } = React.useContext(Context)

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
            // mix the highlight style
            const nameStyle = { ...channelStyle.name.available }
            // and apply it
            setPolish(nameStyle)
            // all done
            return
        }

        // and one for removing the highlight
        const reset = () => {
            // reset the polish
            setPolish(null)
            // all done
            return
        }

        const select = () => {
            // assemble the channel spec
            const spec = { reader, dataset, channel }
            // and adjust the contexts of the active view
            viewChannel(spec)
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