// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useArchive } from './useArchive'
import { useGetActiveView } from '../explorer/useGetActiveView'
// components
import { File } from './file'
import { Folder } from './folder'


// the panel with the contents of the folder at {uri}, read off the archive tree
export const Directory = ({ uri }) => {
    // get the archive
    const archive = useArchive()
    // get the active view information
    const { reader: activeReader } = useGetActiveView()
    // the entries of this folder are the items it holds
    const entries = archive.items.filter(item => item.parent === uri)
    // build a function that determines the state of my folders
    const state = (uri) => activeReader?.uri.startsWith(uri + "/") ? "selected" : "active"
    // render
    return (
        <>
            {entries.map(item => (
                item.isFolder ?
                    <Folder key={item.id} item={item} state={state(item.uri)} />
                    :
                    <File key={item.id} uri={item.uri} name={item.name} />
            ))}
        </>
    )
}


// end of file
