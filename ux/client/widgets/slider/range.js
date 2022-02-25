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
import { Interval } from './interval'
import { Labels } from './labels'
import { Major } from './major'
import { Marker } from './marker'
import { Rangemat } from './rangemat'


// export the slider
export const Range = ({ value, setValue, enabled, ...config }) => {
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
        <Rangemat setValue={setValue} enabled={enabled} >
            <Major />
            <Axis />
            <Labels enabled={enabled} />
            <Interval value={value} enabled={enabled} />
            <Marker id={0} value={value[0]} enabled={enabled} />
            <Marker id={1} value={value[1]} enabled={enabled} />
        </Rangemat>
    )
}


// end of file
