// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from 'react'

// project
// shapes
import { Plus as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'
// styles
import { connect as paintConnect } from './styles'


// control to connect a new data archive
export const Connect = () => {
    // connect a new archive
    const connect = evt => {
        // stop this event from propagating
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // show me
        console.log("connecting a new archive")
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