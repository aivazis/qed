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
import { usePersistArchive } from './usePersistArchive'
// styles
import { persist as paintPersist } from './styles'


// control to write a data archive into the configuration files
// nothing about an archive is saved on its own: not that it is connected, and not what it
// has on display. this is how the user says that the archive, as it stands, is worth keeping
export const Persist = ({ uri, dirty }) => {
    // get the handler that saves the archive
    const { persist } = usePersistArchive()
    // build the handler that reacts to the click
    const save = evt => {
        // this control lives in the header of a tray, so keep the click from toggling it
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // an archive that says what the configuration files say has nothing to save
        if (!dirty) {
            // so there is nothing to do
            return
        }
        // otherwise, send the mutation to the server
        persist({ uri })
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        onClick: save,
    }
    // the glyph fills its box, unlike the ring of the refresh control next to me, so it takes
    // a smaller box to come out the same size
    const size = 12
    // i am available when saving would change something; the handler stays installed either
    // way, so that a click on me never reaches the tray
    const state = dirty ? "enabled" : "disabled"
    // render
    return (
        <Badge size={size} state={state} behaviors={behaviors} style={paintPersist}
            aria-label="save this archive" aria-disabled={!dirty}>
            <Icon />
        </Badge>
    )
}


// end of file
