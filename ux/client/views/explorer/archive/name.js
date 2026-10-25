// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// components
import { EnabledInput, Field, Value } from '../form'

// the name the archive; an archive that exists already keeps its name, so it is {fixed}
export const Name = ({ value, update, fixed = false }) => {
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
    // a name that cannot change
    if (fixed) {
        // shows, but takes no input
        return (
            <Field name="nickname" value={value} tip="the name of the data archive, which stays">
                <Fixed>{value}</Fixed>
            </Field>
        )
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


// a name that takes no input
const Fixed = styled(Value)`
    color: hsl(0deg, 0%, 60%);
    padding: 0.0rem 0.25rem 0.0rem 0.25rem;
`


// end of file
