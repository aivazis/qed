// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'


// local
// components
import { Field, Values, enumValue } from '../form'

// the set of supported filters
export const Filters = ({ value, update, types }) => {
    // validate my contents
    const ok = value.size ? "ok" : ""
    // make a handler that sets the region type
    const toggle = type => {
        // if {value} already contains this filter type
        if (value.has(type)) {
            // build a handler that removes it
            return () => {
                // copy the current value
                const clone = new Set([...value])
                // remove the value
                clone.delete(type)
                // update the form
                update("filters", clone)
                // all done
                return
            }
        }
        // otherwise, build a handler that adds it
        return () => {
            // copy the current value
            const clone = new Set([...value])
            // add the value
            clone.add(type)
            // update the form
            update("filters", clone)
            // all done
            return
        }
    }
    // render
    return (
        <Field name="filters" value={ok} tip="select the search filters">
            <Values>
                {Object.keys(types).map(type => (
                    <Type
                        key={type}
                        name={type} rep={type} current={value} toggle={toggle} />
                ))}
            </Values>
        </Field>
    )
}


// the filter type
const Type = ({ name, rep, current, toggle }) => {
    // assemble the behaviors
    const behaviors = {
        onClick: toggle(rep),
    }
    // deduce my state
    const state = current.has(rep) ? "selected" : "enabled"
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
