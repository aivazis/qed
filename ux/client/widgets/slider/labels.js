// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// external
import React from "react"


// locals
// hooks
import { useConfig } from './useConfig'
// components
import { Label } from './label'


// render the labels
export const Labels = ({ value, setValue, enabled }) => {
    // get the major tick marks
    const { major } = useConfig()

    // render
    return (
        <>
            {major.map(tick => (
                <Label key={tick}
                    tick={tick} value={value} setValue={setValue} enabled={enabled} />
            ))}
        </>
    )
}


// end of file
