// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// setup the flex context
export const ViewportContext = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // the camera position
        position: null,
        setPosition: () => { throw new Error(complaint) }
    }
)


// the provider factory
export const ViewportProvider = ({
    // children
    children
}) => {
    // set up the camera position
    const [position, setPosition] = React.useState({ x: 0, y: 0, z: 0 })

    // assemble the context value
    const context = {
        // camera position
        position, setPosition,
    }

    // provide for my children
    return (
        <ViewportContext.Provider value={context} >
            {children}
        </ViewportContext.Provider >

    )
}


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viewport' context: no provider"


// end of file
