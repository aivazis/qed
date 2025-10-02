// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'

// local
// components
import { Field, Value, Numeric, SpacerFirst, SpacerRest } from '../form'


// collect the coordinates of a point of interest
export const Circle = ({ longitude, latitude, radius, update }) => {
    // check the value
    const valid = longitude === "" || latitude == "" || radius == "" ? "" : "ok"
    // build the radius mutator
    const updateRadius = current => {
        // build the event handler
        const set = evt => {
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
            // build the point
            const circle = {
                // copy the longitude
                longitude,
                // copy the latitude
                latitude,
                // compete the radius
                radius: candidate === "" || regex.test(candidate) ? candidate : current,
            }
            // update the form state
            update("circle", circle)
            // all done
            return
        }
        // and return it
        return set
    }
    // build the longitude mutator
    const updateLongitude = current => {
        // build the event handler
        const set = evt => {
            // get the value from the form field
            const candidate = evt.target.value
            // the validation regex; checks for numbers in [-180, 180]
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
            // build the circle
            const circle = {
                // copy the radius
                radius,
                // copy the latitude
                latitude,
                // compete the longitude
                longitude: candidate === "" || regex.test(candidate) ? candidate : current,
            }
            // update the form state
            update("circle", circle)
            // all done
            return
        }
        // and return it
        return set
    }
    // build the latitude mutator
    const updateLatitude = current => {
        // build the event handler
        const set = evt => {
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
            // build the circle
            const circle = {
                // copy the radius
                radius,
                // copy the longitude
                longitude,
                // compete the latitude
                latitude: candidate === "" || regex.test(candidate) ? candidate : current,
            }
            // update the form state
            update("circle", circle)
            // all done
            return
        }
        // and return it
        return set
    }

    // the behavior of the radius field
    const setRadius = {
        onChange: updateRadius(radius)
    }
    // the behavior of the longitude field
    const setLongitude = {
        onChange: updateLongitude(longitude)
    }
    // the behavior of the latitude field
    const setLatitude = {
        onChange: updateLatitude(latitude)
    }

    // render
    return (
        <Field name="circle" value={valid} tip="the center and radius of the circle of interest">
            <Value>
                <SpacerFirst title="positive number, in meters">radius:</SpacerFirst>
                <Numeric
                    title="positive number, in meters"
                    type="text" value={radius}
                    {...setRadius}
                />
                <SpacerRest title="decimal degrees in [-180, 180]">longitude:</SpacerRest>
                <Numeric
                    title="decimal degrees in [-180, 180]"
                    type="text" value={longitude}
                    {...setLongitude}
                />
                <SpacerRest title="decimal degrees in [-90, 90]">latitude:</SpacerRest>
                <Numeric
                    title="decimal degrees in [-90, 90]"
                    type="text" value={latitude}
                    {...setLatitude}
                />
            </Value>
        </Field>
    )
}



// end of file
