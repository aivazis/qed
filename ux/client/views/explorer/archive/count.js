// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// components
import { Field, Value, Numeric } from '../form'


// information about a data granule
export const Count = ({ form, update }) => {
    // unpack the granule
    const count = form.count
    // validate my contents
    const ok = (count !== "") ? "ok" : ""
    // render
    return (
        <Field
            name="Count" value={ok}
            tip="upper bound on the number of datasets to retrieve"
        >
            <Limit form={form} update={update} />
        </Field>
    )
}


// data entry
const Entry = styled(Numeric)`
`

// the limit
const Limit = ({ form, update }) => {
    // specialize the update
    const setLimit = evt => {
        // get the value
        const candidate = evt.target.value
        // compete the value and update the form
        update("count", (candidate === "" || regex.test(candidate)) ? candidate : form.count)
        // all done
        return
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setLimit
    }
    // render
    return (
        <Value>
            <Entry type="text" value={form.count} {...behaviors} />
        </Value>
    )
}


// the validation regex
const regex = new RegExp([
    "^", // the beginning of the string
    "\\d*", // the integer part
    "$", // the end of the string
].join(''))


// end of file
