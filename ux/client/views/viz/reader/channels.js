// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// project
//widgets
import { Meta } from '~/widgets'

// locals
// hooks
import { useIsActive } from './useIsActive'
import { useChannel } from './useChannel'
// components
import { Channel } from './channel'
// styles
import styles from './styles'


// display the bindings associated with this selector
export const Channels = ({ children }) => {
    // get the selection status of my reader
    const active = useIsActive()
    // and the current channel
    const channel = useChannel()

    // a mark is required if the channel setting in the view is mine and there is no
    // channel selection
    const mark = active && !channel
    // make a label that is marked as required when there is no selected channel
    const label = (
        <span>
            {mark ? <span style={styles.mark}>*</span> : null}
            channels
        </span>
    )

    // mix my paint
    const channelStyle = styles.channels()
    // and render
    return (
        <Meta.Entry attribute={label} style={channelStyle}>
            {children.map(channel => (
                <Channel key={channel.id} channel={channel} />
            ))}
        </Meta.Entry>
    )
}


// end of file
