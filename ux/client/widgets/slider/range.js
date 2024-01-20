// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Provider } from './context'
// components
import { Axis } from './axis'
import { Interval } from './interval'
import { Labels } from './labels'
import { Major } from './major'
import { Minor } from './minor'
import { Marker } from './marker'
import { MarkerLabel } from './markerLabel'
import { Rangemat } from './rangemat'


// export the slider
export const Range = ({ value, setValue, ...config }) => {
    // set up my context and embed my panel
    return (
        <Provider config={config}>
            <Controller value={value} setValue={setValue} />
        </Provider>
    )
}


// render the controller
const Controller = ({ value, setValue }) => {
    // render
    return (
        <Rangemat setValue={setValue} >
            <Major />
            <Minor />
            <Axis />
            <Labels />
            <Interval value={value} />
            <Marker id={0} value={value[0]} />
            <MarkerLabel value={value[0]} />
            <Marker id={1} value={value[1]} />
            <MarkerLabel value={value[1]} />
        </Rangemat>
    )
}


// end of file
