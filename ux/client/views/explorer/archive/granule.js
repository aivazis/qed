// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// components
import { Field, Value, SpacerBetween, EnabledInput } from '../form'


// information about a data granule
export const Granule = ({ form, update }) => {
    // unpack the granule
    const { pattern } = form.granule
    // validate my contents
    const ok = (pattern !== "") ? "ok" : ""
    // render
    return (
        <Field
            name="granule" value={ok}
            tip="the name of the data product; wildcards *? are ok "
        >
            <Name form={form} update={update} />
        </Field>
    )
}


// header
const Header = styled.span`
    display: inline-block;
    width: 6.0em;
    text-align: end;
    vertical-align: bottom;
    padding: 0.0rem 0.0 0.0rem 0.0rem;
    margin: 0.0rem 0.0rem 0.0rem 0.0rem;
    cursor: default;
`

// data entry
const Entry = styled(EnabledInput)`
`

// the granule name
const Name = ({ form, update }) => {
    // specialize the update
    const setName = evt => {
        // get the value
        const pattern = evt.target.value.toUpperCase()
        // build the new granule
        const granule = { ...form.granule, pattern }
        // and update the form
        update("granule", granule)
        // all done
        return
    }
    // assemble my behaviors
    const behaviors = {
        onChange: setName
    }
    // render
    return (
        <Value>
            <Entry type="text" value={form.granule.pattern} {...behaviors} />
        </Value>
    )
}



// end of file
