// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// components
import { Timestamp } from './timestamp'
import { Field, Value } from '../form'


// collect a time interval
export const When = ({ interval, update }) => {
    // unpack the point
    const { begin, end } = interval
    // check the value
    const valid = (begin === "" || end == "") ? "" : "ok"
    // specialize the form update
    const updateWhen = interval => update("when", interval)
    // render
    return (
        <Field name="time" value={valid} tip="the time interval of interest">
            <Value>
                <Box>
                    <Spacer title="a timestamp in YYYY-MM-DD HH:mm:ss">from:</Spacer>
                    <Timestamp interval={interval} field="begin" update={updateWhen} />
                </Box>
                <Box>
                    <Spacer title="a timestamp in YYYY-MM-DD HH:mm:ss">until:</Spacer>
                    <Timestamp interval={interval} field="end" update={updateWhen} />
                </Box>
            </Value>
        </Field>
    )
}


// the container
const Box = styled.div`
`

// the spacer
const Spacer = styled.span`
    display: inline-block;
    width: 3rem;
    text-align: end;
    padding: 0.0rem 0.25rem 0.25rem 0.0rem;
`


// end of file
