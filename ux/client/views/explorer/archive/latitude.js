// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'

// local
// components
import { Numeric } from '../form'


// collect the latitude of a region of interest
export const Latitude = ({ region, update }) => {
    // unpack the region
    const { latitude, ...rest } = region
    // build the latitude mutator
    const set = () => {
        // build the event handler
        const handler = evt => {
            // get the value from the form field
            const candidate = evt.target.value
            // the validation regex; checks for numbers in [-90, 90]
            const regex = new RegExp([
                "^", // the beginning of the string
                "[+-]?", // optional sign
                "(?:", // followed by
                "90(?:\\.0*)?", // the interval edges
                "|", // or
                "(?:(?:[0-9]|[1-8][0-9])(?:\\.\\d*)?)", // numbers in (-90, 90)
                ")?",
                "$", // the end of the string
            ].join(''))
            // build the new region
            const replacement = {
                // unpack the rest of the region properties
                ...rest,
                // compete the latitude
                latitude: candidate === "" || regex.test(candidate) ? candidate : latitude,
            }
            // update the form state
            update(replacement)
            // all done
            return
        }
        // and return it
        return handler
    }
    // the behaviors of the latitude field
    const behaviors = {
        onChange: set()
    }
    // render
    return (
        <Numeric
            title="decimal degrees in [-90, 90]" type="text"
            value={latitude}
            {...behaviors}
        />
    )
}


// end of file
