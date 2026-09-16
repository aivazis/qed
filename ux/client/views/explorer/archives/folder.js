// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
// project
// widgets
import { Tray } from '~/widgets'

// locals
// hooks
import { useArchive } from './useArchive'
import { useExpandFolder } from './useExpandFolder'
import { useCollapseFolder } from './useCollapseFolder'
// components
import { Directory } from './directory'
import { Failure } from './failure'


// a folder of a data archive: a tray the server keeps the state of
export const Folder = ({ item, state }) => {
    // get the archive
    const archive = useArchive()
    // get the tree operations
    const expand = useExpandFolder()
    const collapse = useCollapseFolder()
    // unpack the item
    const { name, uri, expanded, pending, error } = item
    // toggling the tray asks the server to put the folder on display, or take it off
    const toggle = open => (open ? expand : collapse)({ archive: archive.uri, uri })
    // tray paint
    const paint = {
        '--indent': '1em',
        '--header-background': 'hsl(0deg, 0%, 7%, 1)',
        '--header-selected': 'hsl(0deg, 0%, 7%, 1)',
    }
    // render
    return (
        <Tray title={name} state={state} expanded={expanded} onToggle={toggle} busy={pending}
            style={paint} scale={.5}
        >
            {error && <Failure reason={error} />}
            <Directory uri={uri} />
        </Tray>
    )
}


// end of file
