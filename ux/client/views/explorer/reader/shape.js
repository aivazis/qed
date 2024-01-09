// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
// theme
import { theme } from '~/palette'
// local
// components
import { Row, Prompt, Separator, Required, Value, Numeric } from '../form'

// the shape of the data product
export const Shape = ({ lines, samples, update }) => {
    // build the shape mutator
    const setValue = (field, value) => {
        // make the event handler
        const set = evt => {
            // set up the validation regex
            const regex = /^[\d().*\/+-]*$/g
            // get the value
            const candidate = evt.target.value
            // update the form state
            update(field, regex.test(candidate) ? candidate : value)
        }
        // and return it
        return set
    }
    // assemble my behaviors
    const setLines = {
        onChange: setValue("lines", lines),
    }
    const setSamples = {
        onChange: setValue("samples", samples),
    }
    // check whether i have enough
    const invalid = (
        lines === null || lines.length <= 1 || samples === null || samples.length <= 1
    )
    // all done
    return (
        <Row>
            <Prompt title="the shape of the data product">
                {invalid && <Required>*</Required>}
                shape
            </Prompt>
            <Separator>:</Separator>
            <Value>
                <Numeric type="text" value={lines === null ? "" : lines} {...setLines} />
                {" "}
                lines,
                {" "}
                <Numeric type="text" value={samples === null ? "" : samples} {...setSamples} />
                {" "}
                samples
            </Value>
        </Row>
    )
}


// end of file