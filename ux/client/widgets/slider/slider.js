// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// geometry
import { layout } from './layout'
// components
import { Axis } from './axis'
import { Labels } from './labels'
import { Major } from './major'
import { Marker } from './marker'
import { Placemat } from './placemat'
// context
import { Provider } from './context'


// export the Slider
export const Slider = (props) => {
    // set up my context and embed my panel
    return (
        <Provider>
            <Controller {...props} />
        </Provider>
    )
}


//  display the zoom control
const Controller = ({ value, setValue, enabled, ...config }) => {
    // construct the layout
    const geometry = layout(config)
    // render
    return (
        <Placemat setValue={setValue} geometry={geometry} enabled={enabled} >
            <Major geometry={geometry} />
            <Axis geometry={geometry} />
            <Labels value={value} setValue={setValue} geometry={geometry} enabled={enabled} />
            <Marker geometry={geometry} value={value} enabled={enabled} />
        </Placemat>
    )
}

// end of file
