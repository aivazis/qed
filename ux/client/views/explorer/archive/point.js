// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'

// local
// components
import { Latitude } from './latitude'
import { Longitude } from './longitude'
import { Field, Value, SpacerFirst, SpacerBetween } from '../form'


// collect the coordinates of a point of interest
export const Point = ({ region, update }) => {
    // unpack the point
    const { longitude, latitude } = region
    // check the value
    const valid = longitude === "" || latitude == "" ? "" : "ok"
    // specialize the form update
    const updatePoint = (point) => update("point", point)
    // render
    return (
        <Field name="point" value={valid} tip="the coordinates the point of interest">
            <Value>
                <SpacerFirst title="decimal degrees in [-180, 180]">longitude:</SpacerFirst>
                <Longitude region={{ longitude, latitude }} update={updatePoint} />
                <SpacerBetween title="decimal degrees in [-90, 90]">latitude:</SpacerBetween>
                <Latitude region={{ longitude, latitude }} update={updatePoint} />
            </Value>
        </Field>
    )
}


// end of file
