// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'

// local
// components
import { Numeric } from '../form'


// collect the longitude of a region of interest
export const Longitude = ({ region, update }) => {
    // unpack the region
    const { longitude, ...rest } = region
    // build the longitude mutator
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
                "180(?:\\.0*)?", // the interval edges
                "|", // or
                "(?:(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:\\.\\d*)?)", // numbers in (-180, 180)
                ")?",
                "$", // the end of the string
            ].join(''))
            // build the new region
            const replacement = {
                // unpack the rest of the region properties
                ...rest,
                // compete the longitude
                longitude: candidate === "" || regex.test(candidate) ? candidate : longitude,
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
        <Numeric
            title="decimal degrees in [-180, 180]" type="text"
            value={longitude}
            {...behaviors}
        />
    )
}


// end of file
