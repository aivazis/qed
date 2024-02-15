// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// components
import { Row, Prompt, Separator, Required } from './form'

// render a field
export const Field = ({ name, value, tip, required = true, children }) => {
    // check validity
    const invalid = value === null || value.toString().length == 0
    // render
    return (
        <Row>
            <Prompt title={tip}>
                {required && invalid && <Required>*</Required>}
                {name}
            </Prompt>
            <Separator>{name && ":"}</Separator>
            {children}
        </Row>
    )
}


// end of file
