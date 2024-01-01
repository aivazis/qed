// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// components
import { EnabledInput, Field, Value } from '../form'

// the name the archive
export const Name = ({ value, update }) => {
    // build the name mutator
    const setName = evt => {
        // set up the validation regex
        const regex = /^[\w_]?[\w\d@$()_-]*$/g
        // get the value
        const candidate = evt.target.value
        // update the form state
        update("name", regex.test(candidate) ? candidate : value)
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setName,
    }
    // all done
    return (
        <Field name="nickname" value={value} tip="the name of the data archive">
            <Value>
                <EnabledInput type="text" value={value === null ? "" : value} {...behaviors} />
            </Value>
        </Field>
    )
}


// end of file