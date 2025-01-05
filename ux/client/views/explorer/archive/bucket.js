// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'

// local
// components
import { EnabledInput, Field, Value } from '../form'

// the AWS bucket with the data products
export const Bucket = ({ value, update }) => {
    // build the bucket mutator
    const setBucket = evt => {
        // set up the validation regex
        const regex = /^[\w_]?[\w\d_-]*$/g
        // get the value
        const candidate = evt.target.value
        // update the form state
        update("bucket", regex.test(candidate) ? candidate : value)
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setBucket,
    }
    // all done
    return (
        <Field name="bucket" required={false}
            value={value} tip="the AWS bucket with the data products">
            <Value>
                <EnabledInput type="text" value={value === null ? "" : value} {...behaviors} />
            </Value>
        </Field>
    )
}


// end of file