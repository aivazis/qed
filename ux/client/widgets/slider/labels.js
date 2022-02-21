// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"
import styled from 'styled-components'


// locals
// components
import { Label } from './label'


// render the labels
export const Labels = ({ value, setValue, geometry, enabled }) => {
    // get the major tick marks
    const { major } = geometry

    // render
    return (
        <>
            {major.map(tick => (
                <Label key={tick}
                    tick={tick} value={value} setValue={setValue}
                    geometry={geometry} enabled={enabled} />
            ))}
        </>
    )
}


// end of file
