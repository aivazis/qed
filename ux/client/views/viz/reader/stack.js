// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Meta, Slider, SVG } from '~/widgets'

// local
// context
import { Context } from './context'
// hooks
import { useSetStackIndex } from './useSetStackIndex'
// styles
import styles from './styles'


// display a stack member selector
export const Stack = () => {
    // get my stack details from the reader context
    const { stackExtent, stackIndex } = React.useContext(Context)
    // the mutation that pins or clears a member
    const setStackIndex = useSetStackIndex()

    // if i am not a stack, or the stack has too few members to be interesting
    if (!stackExtent || stackExtent < 2) {
        // there is nothing to show
        return null
    }

    // my members are indexed from zero to one less than my extent
    const max = stackExtent - 1
    // the tick marks, one per member
    const major = [...Array(stackExtent).keys()]

    // controller configuration
    const opt = {
        // the marker sits on the pinned member; collective leaves it unpinned
        value: stackIndex,
        // a click pins the chosen member, or clears the pin if it is already pinned
        setValue: raw => {
            // round to a whole member
            const member = Math.round(raw)
            // ignore anything off the scale
            if (member < 0 || member > max) {
                // nothing to do
                return
            }
            // clicking the pinned member clears the pin; otherwise pin the chosen one
            setStackIndex(member === stackIndex ? null : member)
        },
        min: 0, max, major,
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
