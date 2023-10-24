// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from 'react'

// project
// shapes
import { X as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'
// styles
import { disconnect as paintDisconnect } from './styles'


// control to connect a new data archive
export const Disconnect = ({ uri }) => {
    // connect a new archive
    const connect = evt => {
        // stop this event from propagating
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // show me
        console.log(`disconnecting ${uri}`)
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        onClick: connect,
    }
    // render
    return (
        <Badge size={10} state="enabled" behaviors={behaviors} style={paintDisconnect}>
            <Icon />
        </Badge>

    )
}

// end of file