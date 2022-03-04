// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from 'react'


// the provider factory
export const Provider = ({ children }) => {
    // storage for my collection of points
    const [points, setPoints] = React.useState([])
    // the set of selected nodes
    const [selection, setSelection] = React.useState(new Set())
    // a flag that indicates that the user has started dragging a {mark}
    const [moving, setMoving] = React.useState(null)

    // build the initial context value
    const context = {
        // the points that make up the profile
        points, setPoints,
        // selected nodes
        selection, setSelection,
        // movement indicator
        moving, setMoving,
    }

    // provide from my children
    return (
        <Context.Provider value={context} >
            {children}
        </Context.Provider>
    )
}


// set up the {marker} context
export const Context = React.createContext(
    // the default value clients see when accessing the context outside a provider
    {
        // the points that make up the profile
        points: null,
        setPoints: () => { throw new Error(complaint) },
        // selected nodes
        selection: null,
        setSelection: () => { throw new Error(complaint) },
        // movement
        moving: null,
        setMoving: () => { throw new Error(complaint) },
    }
)


// the error message that consumers see when accessing the context outside a provider
const complaint = "while accessing the 'slider' context: no provider"


// end of file
