// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'

// project
// shapes
import { Download as Icon } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// hooks
import { usePersistReader } from './usePersistReader'
// styles
import { persist as paintPersist } from './styles'


// control to write a reader into the configuration files
// nothing about a reader is saved on its own: not that it is connected, and not the state of
// its controllers. this is how the user says that the reader, as it stands, is worth keeping
export const Persist = ({ name }) => {
    // get the handler that saves the reader
    const { persist } = usePersistReader(name)
    // build the handler that reacts to the click
    const save = evt => {
        // this control lives in the header of a tray, so keep the click from toggling it, and
        // from selecting the reader
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // send the mutation to the server
        persist()
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        onClick: save,
    }
    // the glyph fills its box, so it takes a small one to sit well next to its neighbors
    const size = 12
    // render
    return (
        <Badge size={size} state="enabled" behaviors={behaviors} style={paintPersist}
            aria-label={`save '${name}'`}>
            <Icon />
        </Badge>
    )
}


// end of file
