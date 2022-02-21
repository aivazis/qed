// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

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
const Controller = ({ value, setValue, ...config }) => {
    // state
    const enabled = true

    // construct the layout
    const geometry = layout(config)
    // unpack
    const { place } = geometry

    // render
    return (
        <g transform={place} >
            <Placemat geometry={geometry} />
            <Major geometry={geometry} />
            <Axis geometry={geometry} />
            <Labels value={value} setValue={setValue} geometry={geometry} enabled={enabled} />
            <Marker geometry={geometry} value={value} enabled={enabled} />
        </g>
    )
}

// end of file
