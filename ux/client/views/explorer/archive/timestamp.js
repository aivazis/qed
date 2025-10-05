// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// local
// components
import { EnabledInput } from '../form'


// collect a (partial) timestamp
export const Timestamp = ({ interval, field, update }) => {
    // build the interval mutator
    const set = () => {
        // build the event handler
        const handler = evt => {
            // get the value from the form field
            const candidate = evt.target.value
            // build the new region
            const replacement = {
                // unpack the rest of the region properties
                ...interval,
                // compete my field
                [field]: candidate === "" || regex.test(candidate) ? candidate : interval[field],
            }
            // update the form state
            update(replacement)
            // all done
            return
        }
        // and return it
        return handler
    }
    // the behaviors of the longitude field
    const behaviors = {
        onChange: set()
    }
    // render
    return (
        <Stamp
            title="a timestamp in YYYY-MM-DD HH:mm:ss" type="text"
            value={interval[field]}
            {...behaviors}
        />
    )
}


// the input field
const Stamp = styled(EnabledInput)`
    width: 12rem;
`

// the timestamp regular expression
// the parts
const YEAR = /2(?:0(?:\d(?:\d)?)?)?/
const MONTH = /(?:-(?:(?:0\d?)|(?:1[0-2]?))?)?/
const DAY = /(?:-(?:(?:3[01]?)|(?:[1-2]\d?)|(?:0[1-9]?))?)?/
const SEP = /(?:\s+)?/
const HOUR = /(?:(?:[01]\d?)|(?:2[0-3]?))?/
const MINUTE = /(?::(?:[0-5]\d?)?)?/
const SECOND = /(?::(?:[0-5]\d?)?)?/
// putting it all together
const regex = new RegExp(
    `^` +
    `${YEAR.source}${MONTH.source}${DAY.source}` +
    `${SEP.source}` +
    `${HOUR.source}${MINUTE.source}${SECOND.source}` +
    `$`
)
// show me
console.log(regex.source)


// end of file
