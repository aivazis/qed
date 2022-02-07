// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useFetchAllReaders } from './useFetchAllReaders'


// the provider factory
export const Provider = ({ children }) => {
    // ask the server for the known data sources
    const sources = useFetchAllReaders()
    // attach them as read-only state
    const [readers] = React.useState(sources)

    // the shared camera is a ref so that its updates don't force render
    const camera = React.useRef({ x: 0, y: 0, z: 1 })
    // initialize the set viewports; this is where the refs of the mosaic placemats live
    // which are needed for the implementation of the shared camera
    const viewports = React.useRef([])
    // the ref registrar gets called by react when the placemat ref is created; ours just update
    // the corresponding entry in the array of {viewports}; each panel gets its own registrar
    // that knows its positioning in the flex container
    const viewportRegistrar = idx => ref => viewports.current[idx] = ref

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
        viewports, viewportRegistrar,
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
        // the registrar
        viewportRegistrar: () => { throw new Error(complaint) },

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


// the empty view template
export const emptyView = () => ({ reader: null, dataset: null, channel: null })

// the default synced state
export const syncedDefault = false

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viz' context: no provider"


// end of file
