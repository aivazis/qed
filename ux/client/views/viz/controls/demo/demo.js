// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Range, SVG, Tray } from '~/widgets'


//  display the demo control
export const Demo = () => {
    // interval state
    const [interval, setInterval] = React.useState([1, 3])
    // demos are always on
    const enabled = true

    // set the demo level range
    const [min, max] = [0, 5]
    // set up the tick marks
    const major = [...Array(max - min + 1).keys()].map((_, idx) => min + idx)
    // const major = [...Array(max - min + 1).keys()].map((_, idx) => min + idx)
    const range = {
        value: interval, setValue: setInterval,
        min, max, major,
        direction: "row", labels: "top", arrows: "bottom",
        height: 100, width: 250,
    }

    // and render
    return (
        <Tray title="demo" state="enabled" initially={true}>
            {/* the control housing */}
            <Housing height={range.height} width={range.width}>
                {/* the range slider */}
                <RangeController enabled={enabled} {...range} />
            </Housing>
        </Tray>
    )
}


// the slider housing
const Housing = styled(SVG)`
    margin: 1.0rem auto;
`


// the controllers
const RangeController = styled(Range)`
`


// end of file
