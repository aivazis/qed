// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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

    // build the current value of the context
    const context = {
        // the active view and its mutator
        activeViewport, setActiveViewport,
        // the set of active viewports (actually, the {mosaic} placemats)
        viewports, viewportRegistrar,
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
    }
)

// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'main' context: no provider"


// end of file
