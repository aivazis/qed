// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'

// local
// hooks
import { useGetAvailableArchiveTypes } from '../explorer/useGetAvailableArchiveTypes'
// components
import {
    Field,
    Values,
    enumValue,
} from '../form'

// the archive type selector
export const TypeSelector = ({ value, update }) => {
    // ask the server for the available archive types
    const availableArchiveTypes = useGetAvailableArchiveTypes()
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
                {availableArchiveTypes.map(({ name, label }) => (
                    <Type key={label} name={label} rep={name} current={value} select={select} />
                ))}
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
