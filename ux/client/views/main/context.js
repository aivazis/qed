// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// the provider factory
export const Provider = ({ children }) => {
    // setup the activity panel flag
    const [activityPanel, setActivityPanel] = React.useState(true)

    // a table with the sync status of the current viewports
    const [synced, setSynced] = React.useState([syncedDefault])
    // a table with the zoom levels of the current viewports
    const [zoom, setZoom] = React.useState([zoomDefault])

    // the measuring layer state
    const [measureLayer, setMeasureLayer] = React.useState([measureDefault])
    // storage for the collection of pixels in a {measure} layer profile
    const [pixelPath, setPixelPath] = React.useState([pixelPathDefault()])
    // the set of selected nodes in a {measure} layer profile
    const [pixelPathSelection, setPixelPathSelection] = React.useState(
        [...pixelPathSelectionDefault()])

    // build the current value of the context
    const context = {
        // the activity panel state flag and its mutator
        activityPanel, setActivityPanel,
        // synced views
        synced, setSynced,
        // zoom levels
        zoom, setZoom,
        // the measure layer
        measureLayer, setMeasureLayer,
        // the pixels that make up a measure profile
        pixelPath, setPixelPath,
        // selected nodes
        pixelPathSelection, setPixelPathSelection,

    }
    // provide for my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider >

    )
}

// setup the flex context
export const Context = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // the activity panel state and its mutator
        activityPanel: null,
        setActivityPanel: () => { throw new Error(complaint) },

        // indicators of whether views are synced to the shared camera
        synced: null,
        setSynced: () => { throw new Error(complaint) },
        // the zoom levels of the viewports
        zoom: null,
        setZoom: () => { throw new Error(complaint) },

        // the measure layer flag and its mutator
        measureLayer: null,
        setMeasureLayer: () => { throw new Error(complaint) },
        // the pixels that make up the measure profile
        pixelPath: null,
        setPixelPath: () => { throw new Error(complaint) },
        // selected nodes
        pixelPathSelection: null,
        setPixelPathSelection: () => { throw new Error(complaint) },
    }
)

// the default synced state
export const syncedDefault = {
    channel: false, zoom: false, scroll: false, path: false,
    offset: { x: 0, y: 0 }
}
// the default zoom level
export const zoomDefault = { horizontal: 0, vertical: 0 }
// the default state of the measure layer
export const measureDefault = false
// the default pixel path
export const pixelPathDefault = () => ({ closed: false, points: [] })
// the default pixel path selection
export const pixelPathSelectionDefault = () => [new Set()]

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'main' context: no provider"


// end of file
