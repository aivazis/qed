// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
// project
// shapes
import { Gear } from '~/shapes'
// widgets
import { Badge } from '~/widgets'

// local
// hooks
import { useEditArchive } from '../archive/useEditArchive'
// styles
import { edit as paintEdit } from './styles'


// the button that brings up the form that reconfigures an {archive}
export const Edit = ({ archive }) => {
    // get the form opener
    const editArchive = useEditArchive()
    // build the handler that opens the form
    const edit = evt => {
        // stop this event from propagating
        evt.stopPropagation()
        // and quash any side effects
        evt.preventDefault()
        // bring up the form
        editArchive(archive)
        // all done
        return
    }
    // set up my behaviors
    const behaviors = {
        onClick: edit,
    }
    // render
    return (
        <Badge size={20} state="enabled" behaviors={behaviors} style={paintEdit}
            aria-label="edit this archive">
            <Icon />
        </Badge>
    )
}


// the gear fills its box, so it is shrunk about its center to match the shapes of its neighbors;
// the badge hands its paint to its child, which passes it on to the gear
const Icon = ({ style }) => (
    <g transform="translate(500 500) scale(0.65) translate(-500 -500)">
        <Gear style={style} />
    </g>
)


// end of file
