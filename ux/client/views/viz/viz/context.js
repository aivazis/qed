// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useFetchAllReaders } from './useFetchAllReaders'


// set up the viz context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provider
    {
        // the set of known data sources
        readers: [],
        // the shared camera,
        camera: null,
        // the set of active viewports (actually, the {mosaic} placemats)
        viewports: null,

        // the known views
        views: null,
        setViews: () => { throw new Error(complaint) },
        // the active view
        activeViewport: null,
        setActiveViewport: () => { throw new Error(complaint) },
        // indicators of whether views are synced to the shared camera
        synced: null,
        setSynced: () => { throw new Error(complaint) },
    }
)


// the provider factory
export const Provider = ({ children }) => {
    // ask the server for the known data sources
    const sources = useFetchAllReaders()
    // attach them as read-only state
    const [readers] = React.useState(sources)

    // the shared camera is a ref so that its updates don't force render
    const camera = React.useRef({ x: 0, y: 0, z: 1 })
    // initialized the set viewports
    const viewports = React.useRef([])

    // the set of known views; it starts out with one empty view
    const [views, setViews] = React.useState([emptyView()])
    // the active view is an index into the set of {views}
    const [activeViewport, setActiveViewport] = React.useState(0)
    // a table with the sync status of the known views
    const [synced, setSynced] = React.useState([syncedDefault])

    // build the initial context value
    const context = {
        // the data sources
        readers,
        // the shared camera
        camera,
        // the set of active viewports (actually, the {mosaic} placemats)
        viewports,
        // the known views
        views, setViews,
        // the active view
        activeViewport, setActiveViewport,
        // synced views
        synced, setSynced,
    }

    // provide for my children
    return (
        <Context.Provider value={context}>
            {children}
        </Context.Provider>
    )
}


// the empty view template
export const emptyView = () => null // ({ reader: null, dataset: null, channel: null })

// the default synced state
export const syncedDefault = false

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viz' context: no provider"


// end of file
