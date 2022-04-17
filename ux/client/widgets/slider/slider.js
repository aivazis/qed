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
import { Simplemat } from './simplemat'


// export the slider
export const Slider = ({ value, setValue, ...config }) => {
    // set up my context and embed my panel
    return (
        <Provider config={config}>
            <Controller value={value} setValue={setValue} />
        </Provider>
    )
}


// lay out the control
const Controller = ({ value, setValue }) => {
    // render
    return (
        <Simplemat setValue={setValue} >
            <Major />
            <Axis />
            <Labels value={value} setValue={setValue} />
            <Marker value={value} />
        </Simplemat>
    )
}


// end of file
