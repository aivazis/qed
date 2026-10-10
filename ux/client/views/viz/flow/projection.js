// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// local
// the projections
import { flat } from './flat/projection'
import { makeIso } from './iso/projection'


// build the projection that {spec} asks for: flat, unless it asks for an isometric view; a
// projection maps diagram coordinates to the screen ({project}), a displacement of the pointer
// back onto the floor ({ground}) and into a change of height ({lift}), tells how near a point is
// to the viewer ({depth}), and how far up a label floats ({labelLift})
export const makeProjection = (spec = { kind: "flat" }) => {
    // an isometric view
    if (spec.kind === "iso") {
        // gets built to its settings
        return makeIso(spec)
    }
    // anything else is flat
    return flat
}


// the projection in use
const Context = React.createContext(flat)


// the provider
export const ProjectionProvider = ({ projection = flat, children }) => {
    // provide for my children
    return (
        <Context.Provider value={projection}>
            {children}
        </Context.Provider>
    )
}


// access to the projection in use
export const useProjection = () => {
    // pull it from the context
    return React.useContext(Context)
}


// end of file
