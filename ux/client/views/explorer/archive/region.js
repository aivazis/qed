// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// components
import { EnabledInput, Field, Value } from '../form'

// the AWS region with the data products
export const Region = ({ value, update }) => {
    // build the region mutator
    const setRegion = evt => {
        // set up the validation regex
        const regex = /^[\w_]?[\w\d_-]*$/g
        // get the value
        const candidate = evt.target.value
        // update the form state
        update("region", regex.test(candidate) ? candidate : value)
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setRegion,
    }
    // all done
    return (
        <Field name="region" required={false} value={value}
            tip="the AWS region with the data products">
            <Value>
                <EnabledInput type="text" value={value === null ? "" : value} {...behaviors} />
            </Value>
        </Field>
    )
}


// end of file