// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'

// local
// components
import { EnabledInput, Field, Value } from '../form'

// the path the archive
export const Path = ({ value, update }) => {
    // build the path mutator
    const setPath = evt => {
        // set up the validation regex
        const regex = /^.*$/g
        // get the value
        const candidate = evt.target.value
        // update the form state
        update("path", regex.test(candidate) ? candidate : value)
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setPath,
    }
    // all done
    return (
        <Field name="path" required={false} value={value} tip="the path to the data archive">
            <Value>
                <EnabledInput type="text" value={value === null ? "" : value} {...behaviors} />
            </Value>
        </Field>
    )
}


// end of file