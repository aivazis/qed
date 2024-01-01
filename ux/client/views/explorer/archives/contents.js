// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Tray } from '~/widgets'

// locals
// hooks
import { useGetActiveView } from '../explorer/useGetActiveView'
import { useQueryDirectoryContents } from './useFetchDirectoryContents'
// components
import { Busy } from './busy'
import { Directory } from './directory'
import { File } from './file'

// the panel with the directory contents
export const Contents = ({ qref }) => {
    // get the contents
    const { contents } = useQueryDirectoryContents(qref)
    // get the active view information
    const { reader: activeReader } = useGetActiveView()
    // build a function that determines the state of my items
    const state = (uri) => activeReader?.uri.startsWith(uri + "/") ? "selected" : "active"

    // tray paint
    const paint = {
        '--indent': '1em',
        '--header-background': 'hsl(0deg, 0%, 7%, 1)',
        '--header-selected': 'hsl(0deg, 0%, 7%, 1)',
    }
    // render
    return (
        <>
            {contents.map(item => (
                item.isFolder ?
                    <Tray key={item.id} title={item.name} state={state(item.uri)}
                        initially={false} style={paint} scale={.5}
                    >
                        <React.Suspense fallback={<Busy />}>
                            <Directory uri={item.uri} />
                        </React.Suspense>
                    </Tray >
                    :
                    <File key={item.id} uri={item.uri} name={item.name} />
            ))}
        </>
    )
}


// end of file
