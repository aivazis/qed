// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Range, SVG, Tray } from '~/widgets'


//  display the demo control
export const Demo = () => {
    // manage my state
    const [enabled, setEnabled] = React.useState(true)
    // interval state
    const [interval, setInterval] = React.useState([1, 3])

    // make a toggle
    const toggle = () => setEnabled(old => !old)

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
        <Tray title="demo" state="enabled" initially={true} scale={0.5}>
            {/* state control */}
            <Button type="button" onClick={toggle}>
                {enabled ? "disable" : "enable"}
            </Button>
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

// the controller
const RangeController = styled(Range)`
`

// the state control
const Button = styled.button`
    & {
        cursor: pointer;
        font-family: inconsolata;
        font-size: 75%;
        text-align: start;
        color: hsl(0deg, 0%, 60%);
        background-color: transparent;
        border: 0 transparent;
        margin: 0.0rem 0.0rem 0.0rem 0.25rem;
    }

    &:active {
        color: hsl(28deg, 90%, 55%);
        border: 1 solid hsl(0deg, 0%, 40%);
    }

    &:hover {
        color: hsl(28deg, 90%, 55%);
        border: 1 solid hsl(0deg, 0%, 40%);
    }
`


// end of file
