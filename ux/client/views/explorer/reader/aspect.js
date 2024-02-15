// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// components
import { Row, Prompt, Separator, Value, Numeric } from '../form'

// the shape of the data product
export const Aspect = ({ aspect, update }) => {
    // make the event handler
    const set = evt => {
        // set up the validation regex
        const regex = /^[\d().*\/+-]*$/g
        // get the value
        const candidate = evt.target.value
        // update the form state
        update("aspect", regex.test(candidate) ? candidate : aspect)
        // all done
        return
    }
    // assemble my behaviors
    const behaviors = {
        onChange: set
    }
    // all done
    return (
        <Row>
            <Prompt title="restrict shape guesses to ones with aspect ratio less than this">
                max aspect
            </Prompt>
            <Separator>:</Separator>
            <Value>
                <Numeric type="text" value={aspect === null ? "" : aspect} {...behaviors} />
            </Value>
        </Row>
    )
}


// end of file