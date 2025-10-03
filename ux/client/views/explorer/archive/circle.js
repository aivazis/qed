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
import { Radius } from './radius'
import { Field, Value, SpacerFirst, SpacerRest } from '../form'


// collect the coordinates of a point of interest
export const Circle = ({ longitude, latitude, radius, update }) => {
    // check the value
    const valid = longitude === "" || latitude == "" || radius == "" ? "" : "ok"
    // specialize the form update
    const updateCircle = (circle) => update("circle", circle)
    // render
    return (
        <Field name="circle" value={valid} tip="the center and radius of the circle of interest">
            <Value>
                <SpacerFirst title="positive number, in meters">radius:</SpacerFirst>
                <Radius region={{ longitude, latitude, radius }} update={updateCircle} />
                <SpacerRest title="decimal degrees in [-180, 180]">longitude:</SpacerRest>
                <Longitude region={{ longitude, latitude, radius }} update={updateCircle} />
                <SpacerRest title="decimal degrees in [-90, 90]">latitude:</SpacerRest>
                <Latitude region={{ longitude, latitude, radius }} update={updateCircle} />
            </Value>
        </Field>
    )
}


// end of file
