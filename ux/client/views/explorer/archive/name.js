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
import { Field, Nickname, Value } from '../form'

// the name of the archive, with the server's {suggestion} dimmed while the field is empty; an
// archive that exists already keeps its name, so it is {fixed}
export const Name = ({ value, suggestion = "", update, fixed = false }) => {
    // a name that cannot change
    if (fixed) {
        // shows, but takes no input
        return (
            <Field name="nickname" value={value} tip="the name of the data archive, which stays">
                <Fixed>{value}</Fixed>
            </Field>
        )
    }
    // otherwise, the user picks it
    return (
        <Nickname value={value} suggestion={suggestion} update={update} pattern={pattern}
            tip="the name of the data archive" />
    )
}


// the names an archive can have
const pattern = /^[\w_]?[\w\d@$()_-]*$/

// a name that takes no input
const Fixed = styled(Value)`
    color: hsl(0deg, 0%, 60%);
    padding: 0.0rem 0.25rem 0.0rem 0.25rem;
`


// end of file
