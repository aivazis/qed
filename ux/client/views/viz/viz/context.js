// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// the provider factory
export const VizProvider = ({ children }) => {
    // the active viewport is an index into the set of {views}
    const [activeViewport, setActiveViewport] = React.useState(0)
    // initialize the set of viewports; this is where the refs of the mosaic placemats live
    // which are needed for the implementation of the shared camera
    const viewports = React.useRef([])
    // the ref registrar gets called by react when the placemat ref is created; ours just update
    // the corresponding entry in the array of {viewports}; each panel gets its own registrar
    // that knows its positioning in the flex container
    const viewportRegistrar = idx => ref => viewports.current[idx] = ref
    // the per-viewport opt-in to live sync: a client-only preference that makes a viewport push its
    // interactions to the server live -- on every scroll tick, so peers follow smoothly -- instead
    // of once the gesture settles. off by default; a fast link can turn it on from the viewport bar
    const [live, setLive] = React.useState(() => new Set())
    // flip a viewport's opt-in
    const toggleLive = viewport => setLive(prev => {
        // copy the set so react sees a new reference
        const next = new Set(prev)
        // if the viewport is currently opted in
        if (next.has(viewport)) {
            // opt it out
            next.delete(viewport)
        } else {
            // otherwise, opt it in
            next.add(viewport)
        }
        // hand back the updated set
        return next
    })

    // build the current value of the context
    const context = {
        // the active view and its mutator
        activeViewport, setActiveViewport,
        // the set of active viewports (actually, the {mosaic} placemats)
        viewports, viewportRegistrar,
        // the per-viewport live-sync opt-in and its toggle
        live, toggleLive,
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
        // the active viewport
        activeViewport: null,
        setActiveViewport: () => { throw new Error(complaint) },
        // the set of active viewports (actually, the {mosaic} placemats)
        viewports: null,
        // the registrar
        viewportRegistrar: () => { throw new Error(complaint) },
        // the per-viewport live-sync opt-in and its toggle
        live: new Set(),
        toggleLive: () => { throw new Error(complaint) },
    }
)

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'main' context: no provider"


// end of file
