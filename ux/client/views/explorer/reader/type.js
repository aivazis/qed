// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'

// local
// components
import { Field, Values, enumValue } from '../form'

// the reader type selector
export const Type = ({ value, update }) => {
    // make a handler that sets the reader type
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
        <Field name="type" value={value} tip="select the reader type">
            <Values>
                <Option name="nisar" rep="nisar" current={value} select={select} />
                <Option name="isce2" rep="isce2" current={value} select={select} />
                <Option name="gdal" rep="gdal" current={value} select={select} />
                <Option name="native" rep="native" current={value} select={select} />
            </Values>
        </Field>
    )
}


// the reader type field
const Option = ({ name, rep, current, select }) => {
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