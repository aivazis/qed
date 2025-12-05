// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Meta, Slider, SVG } from '~/widgets'

// local
// styles
import styles from './styles'

// display a stack frame selector
export const Stack = () => {
    // the stack index
    const [index, setIndex] = React.useState(0)
    // and its range
    const [extent, setExtent] = React.useState(5)

    // if we have a trivial stack
    if (extent == 0) {
        // bail
        return null
    }

    // set up the tick marks
    const major = [...Array(extent + 1).keys()]
    // controller configuration
    const opt = {
        value: index,
        setValue: value => setIndex(Math.round(value)),
        min: 0, max: extent, major,
        direction: "row", labels: "bottom", arrows: "top", markers: true,
        height: 75, width: 190,
        tickPrecision: 0, markerPrecision: 0,
    }

    // mix my paint
    const paint = styles.axis()
    // render
    return (
        <Meta.Entry attribute="stack index" style={paint}>
            <Housing height={opt.height} width={opt.width}>
                <Controller enabled={true} {...opt} />
            </Housing>
        </Meta.Entry>
    )
}


// the controller housing
const Housing = styled(SVG)`
`

// the controller
const Controller = styled(Slider)`
`

// end of file
