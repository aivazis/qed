// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// components
import { Field, Value } from '../form'

// the name the archive
export const Cells = ({ value }) => {
    // render
    return (
        <Field name="dataset size" value={value} tip="the size of the dataset">
            <Value>
                {value} cells
            </Value>
        </Field>
    )
}


// end of file