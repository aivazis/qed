// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// components
import { EnabledInput, Field, Value } from '../form'

// the profile of the AWS connection
export const Profile = ({ value, update }) => {
    // build the profile mutator
    const setProfile = evt => {
        // set up the validation regex
        const regex = /^[\w_]?[\w\d_-]*$/g
        // get the value
        const candidate = evt.target.value
        // update the form state
        update("profile", regex.test(candidate) ? candidate : value)
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setProfile,
    }
    // all done
    return (
        <Field name="profile" required={false} value={value}
            tip="the name of the profile with the AWS credentials"
        >
            <Value>
                <EnabledInput type="text" value={value === null ? "" : value} {...behaviors} />
            </Value>
        </Field>
    )
}


// end of file