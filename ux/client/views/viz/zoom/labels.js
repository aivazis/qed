// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"

// locals
// components
import { Label } from "./label"


// the labels
export const Labels = ({ geometry, state }) => {
    // unpack the geometry
    const { min, major } = geometry

    // build the values of the labels
    const labels = new Array(major).fill(null).map((_, idx) => min + idx)

    // render
    return (
        <>
            {labels.map(value => (
                <Label key={value} value={value} state={state} geometry={geometry} />
            ))}
        </>
    )
}


// end of file
