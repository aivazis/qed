// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'

// locals
// context
import { Provider } from './context'
// hooks
import { useConfig } from './useConfig'
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
    // the client names the two thumbs (e.g. "linear low" / "linear high"); fall back to nothing
    const { names = [] } = useConfig()
    // render; the axis, ticks, and tick labels are a decorative scale that duplicates the
    // accessible thumbs (role=slider, aria-valuenow), so they are hidden from assistive tech
    return (
        <Rangemat setValue={setValue} >
            <g aria-hidden="true">
                <Axis />
                <Major />
                <Minor />
                <Labels />
            </g>
            <Interval value={value} />
            <Marker id={0} value={value[0]} name={names[0]} />
            <MarkerLabel value={value[0]} />
            <Marker id={1} value={value[1]} name={names[1]} />
            <MarkerLabel value={value[1]} />
        </Rangemat>
    )
}


// end of file
