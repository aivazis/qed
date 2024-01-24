// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// project
// hooks
import { useConnectArchive } from './useConnectArchive'
// shapes
import { Plus as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// styles
import { connect as paintConnect } from './styles'


// control to connect a new data archive
export const Connect = () => {
    // get the activator
    const collectArchiveInfo = useConnectArchive()
    // connect a new archive
    const connect = evt => {
        // stop this event from propagating
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // collect the new archive info
        collectArchiveInfo()
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        onClick: connect,
    }
    // render
    return (
        <Badge size={10} state="enabled" behaviors={behaviors} style={paintConnect}>
            <Icon />
        </Badge>

    )
}


// end of file