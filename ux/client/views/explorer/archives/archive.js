// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


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
import { useGetActiveView } from '../explorer/useGetActiveView'
// components
import { Directory } from './directory'
import { Disconnect } from './disconnect'
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
    // unpack the archive information
    const { id, name, uri } = archive
    // deduce my state
    const state = (activeArchive?.id === id) ? "selected" : "enabled"
    // build my controls
    const Controls = <Disconnect uri={uri} />
    // mix my paint
    const paint = paintArchive(state)
    // render
    return (
        <Tray title={name} initially={true} state={state} scale={0.5} controls={Controls}>
            <Meta.Table style={paint.meta}>
                <Meta.Entry attribute="uri" style={paint.meta}>
                    {uri}
                </Meta.Entry>
            </Meta.Table>
            <Directory uri={uri} />
        </Tray>
    )
}


// end of file
