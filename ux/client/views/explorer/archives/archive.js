// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from "react"

// project
// widgets
import { Meta, Tray } from '~/widgets'

// locals
// context
import { Provider } from './context'
// hooks
import { useArchive } from './useArchive'
import { useExpandFolder } from './useExpandFolder'
import { useCollapseFolder } from './useCollapseFolder'
import { useGetActiveView } from '../explorer/useGetActiveView'
// components
import { Directory } from './directory'
import { Disconnect } from './disconnect'
import { Failure } from './failure'
import { Persist } from './persist'
import { Refresh } from './refresh'
// styles
import { archive as paintArchive } from './styles'

// turn the panel into a context manager
export const Archive = props => (
    <Provider {...props}>
        <Panel />
    </Provider>
)

// the panel with the archive contents
const Panel = () => {
    // get my details
    const archive = useArchive()
    // unpack the active view
    const { archive: activeArchive } = useGetActiveView()
    // get the tree operations
    const expand = useExpandFolder()
    const collapse = useCollapseFolder()
    // unpack the archive information
    const { id, name, uri, expanded, pending, error, hits } = archive
    // deduce my state
    const state = (activeArchive?.id === id) ? "selected" : "enabled"
    // toggling the tray asks the server to put the root on display, or take it off
    const toggle = open => (open ? expand : collapse)({ archive: uri, uri })
    // build my controls
    const Controls = (
        <>
            <Refresh uri={uri} />
            <Persist uri={uri} />
            <Disconnect uri={uri} />
        </>
    )
    // mix my paint
    const paint = paintArchive(state)
    // render
    return (
        <Tray title={name} expanded={expanded} onToggle={toggle} busy={pending}
            state={state} scale={0.5} controls={Controls}
        >
            <Meta.Table style={paint.meta}>
                <Meta.Entry attribute="uri" style={paint.meta}>
                    {uri}
                </Meta.Entry>
                {hits != null &&
                    <Meta.Entry attribute="hits" style={paint.meta}>
                        {hits}
                    </Meta.Entry>
                }
            </Meta.Table>
            {error && <Failure reason={error} />}
            <Directory uri={uri} />
        </Tray>
    )
}


// end of file
