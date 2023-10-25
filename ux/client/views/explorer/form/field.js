// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// components
import { Row, Prompt, Separator, Required } from './form'

// render a field
export const Field = ({ name, value, tip, children }) => {
    // check validity
    const invalid = value === null || value.toString().length == 0
    // render
    return (
        <Row>
            <Prompt title={tip}>
                {invalid && <Required>*</Required>}
                {name}
            </Prompt>
            <Separator>:</Separator>
            {children}
        </Row>
    )
}


// end of file
