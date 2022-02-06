// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'


// the provider factory
export const Provider = ({
    // children
    children
}) => {
    // set up the camera position
    // N.B.: the separation of {zoom} in a state variable vs {position} in a ref is a performance
    //       enhancement; modifying {position} does not cause the {viewport} to re-render, but
    //       modifying {zoom} must; i have to remember to update the {z} component of {position}
    //       whenever {zoom} is updated
    const [zoom, setZoom] = React.useState(1)
    const position = React.useRef({ x: 0, y: 0, z: zoom })

    // assemble the context value
    const context = {
        // camera position
        zoom, setZoom,
        position,
    }

    // provide for my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider >

    )
}


// setup the viewport context
export const Context = React.createContext(
    // the default value that consumers see when accessing the context outside a provider
    {
        // the camera position
        zoom: null,
        setSoom: () => { throw new Error(complaint) },
        position: null,
    }
)


// the error message to show consumers that are not nested within a provider
const complaint = "while accessing the 'viewport' context: no provider"


// end of file
