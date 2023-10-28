// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// external
import React from 'react'

// local
// components
import {
    Field,
    Values,
    enumValue,
} from '../form'

// the archive type selector
export const TypeSelector = ({ value, update }) => {
    // make a handler that sets the archive type
    const select = type => {
        // build the selector
        return () => {
            // update the form state
            update("type", type)
            // all done
            return
        }
    }
    // render
    return (
        <Field name="type" value={value} tip="select the archive type">
            <Values>
                <Type name="local" rep="local" current={value} select={select} />
                <Type name="s3" rep="s3" current={value} select={select} />
            </Values>
        </Field>
    )
}


// the archive type field
const Type = ({ name, rep, current, select }) => {
    // assemble the behaviors
    const behaviors = {
        onClick: select(rep)
    }
    // deduce my state
    const state = current === rep ? "selected" : "enabled"
    // pick a field selector based on my state
    const Selector = enumValue(state)
    // and render it
    return (
        <Selector {...behaviors}>
            {name}
        </Selector>
    )
}

// end of file