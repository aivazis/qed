// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'


// local
// components
import { Field, Values, enumValue } from '../form'

// the geographic search type selector
export const Geo = ({ value, update, types }) => {
    // make a handler that sets the region type
    const select = type => {
        // build the selector
        return () => {
            // update the form state
            update("geo", type)
            // all done
            return
        }
    }
    // render
    return (
        <Field name="search region" value={value} tip="select the type of region of interest">
            <Values>
                {Object.keys(types).map(type => (
                    <Type
                        key={type}
                        name={type} rep={type} current={value} select={select} />
                ))}
            </Values>
        </Field>
    )
}


// the region type
const Type = ({ name, rep, current, select }) => {
    // assemble the behaviors
    const behaviors = {
        onClick: select(rep),
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
