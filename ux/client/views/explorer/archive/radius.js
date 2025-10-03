// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'

// local
// components
import { Numeric } from '../form'


// collect the radius of a region of interest
export const Radius = ({ region, update }) => {
    // unpack the region
    const { radius, ...rest } = region
    // build the radius mutator
    const set = () => {
        // build the event handler
        const handler = evt => {
            // get the value from the form field
            const candidate = evt.target.value
            // the validation regex; checks for numbers in [-90, 90]
            const regex = new RegExp([
                "^", // the beginning of the string
                "[+]?", // optional sign
                "(?:", // followed by
                "(?:\\d*)?", // the integer part
                "(?:\\.*)?", // the decimal point
                "(?:\\d*)?", // the fractional part
                ")?",
                "$", // the end of the string
            ].join(''))
            // build the new region
            const replacement = {
                // unpack the rest of the region properties
                ...rest,
                // compete the radius
                radius: candidate === "" || regex.test(candidate) ? candidate : radius,
            }
            // update the form state
            update(replacement)
            // all done
            return
        }
        // and return it
        return handler
    }
    // the behaviors of the radius field
    const behaviors = {
        onChange: set()
    }
    // render
    return (
        <Numeric
            title="decimal degrees in [-180, 180]" type="text"
            value={radius}
            {...behaviors}
        />
    )
}


// end of file
