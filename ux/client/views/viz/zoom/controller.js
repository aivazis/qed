// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"

// locals
// components
import { Axis } from "./axis"
import { Indicator } from './indicator'
import { Labels } from './labels'
import { MajorTickmarks } from './majorTickmarks'


// the zoom controller
export const Controller = ({ state, geometry }) => {
    // get my intrinsic length scale out of the control {geometry}
    const { ils } = geometry
    // assemble the parts and render them
    return (
        <g transform={`scale(${ils}) translate(0 50)`}>
            <MajorTickmarks geometry={geometry} />
            <Axis geometry={geometry} />
            <Indicator geometry={geometry} state={state} />
            <Labels geometry={geometry} state={state} />
        </g>
    )
}


// end of file
