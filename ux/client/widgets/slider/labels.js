// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from "react"


// locals
// hooks
import { useConfig } from './useConfig'
// components
import { Label } from './label'


// render the labels
export const Labels = ({ value = null, setValue = null }) => {
    // get the major tick marks
    const { major } = useConfig()

    // render
    return (
        <>
            {major.map(tick => (
                <Label key={tick}
                    tick={tick} value={value} setValue={setValue} />
            ))}
        </>
    )
}


// end of file
