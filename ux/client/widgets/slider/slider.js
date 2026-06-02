// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Provider } from './context'
// components
import { Axis } from './axis'
import { Labels } from './labels'
import { Major } from './major'
import { Minor } from './minor'
import { Marker } from './marker'
import { MarkerLabel } from './markerLabel'
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
    // render; the axis, ticks, and tick labels are a decorative scale that duplicates the
    // accessible thumb (role=slider, aria-valuenow), so they are hidden from assistive tech --
    // they stay clickable for mouse users. the {Marker} thumb stays in the accessible tree.
    return (
        <Simplemat setValue={setValue} >
            <g aria-hidden="true">
                <Axis />
                <Major setValue={setValue} />
                <Minor setValue={setValue} />
                <Labels value={value} setValue={setValue} />
            </g>
            <Marker value={value} />
            <MarkerLabel value={value} />
        </Simplemat>
    )
}


// end of file
