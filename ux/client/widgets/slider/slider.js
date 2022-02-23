// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Provider } from './context'
// components
import { Axis } from './axis'
import { Labels } from './labels'
import { Major } from './major'
import { Marker } from './marker'
import { Placemat } from './placemat'


// export the Slider
export const Slider = ({ value, setValue, enabled, ...config }) => {
    // set up my context and embed my panel
    return (
        <Provider config={config}>
            <Controller value={value} setValue={setValue} enabled={enabled} />
        </Provider>
    )
}


// render the zoom control
const Controller = ({ value, setValue, enabled }) => {
    // render
    return (
        <Placemat setValue={setValue} enabled={enabled} >
            <Major />
            <Axis />
            <Labels value={value} setValue={setValue} enabled={enabled} />
            <Marker value={value} enabled={enabled} />
        </Placemat>
    )
}


// end of file
