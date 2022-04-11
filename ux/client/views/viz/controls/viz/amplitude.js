// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// widgets
import { Range, SVG } from '~/widgets'


// amplitude controller
export const AmplitudeController = props => {
    // unpack the data
    const configuration = useFragment(graphql`
        fragment amplitude_amplitude on AmplitudeController {
            id
            slot
            min
            max
            low
            high
        }
    `, props.configuration)

    // unpack
    const { slot, min, max, low, high } = configuration

    // switch to log scale
    const logMin = Math.round(Math.log10(min))
    const logMax = Math.round(Math.log10(max))
    const logLow = Math.log10(Math.max(min, low))
    const logHigh = Math.log10(Math.min(max, high))
    // set up the tick marks
    const major = [...Array(logMax - logMin + 1).keys()].map((_, idx) => logMin + idx)

    // the value updated
    const setValue = v => console.log(v)
    // controller configuration
    const amplitude = {
        value: [logLow, logHigh], setValue,
        min: logMin, max: logMax, major,
        direction: "row", labels: "bottom", arrows: "top",
        height: 100, width: 250,
    }

    // show me
    console.log(amplitude)

    // render
    return (
        <>
            <Header>
                <Title>{slot}</Title>
            </Header>
            <Housing height={amplitude.height} width={amplitude.width}>
                <Controller enabled={true} {...amplitude} />
            </Housing>
        </>
    )
}


// the section header
const Header = styled.div`
    font-size: 65%;
    margin: 0.5rem 1.0rem 0.25rem 1.0rem;
`

// the title
const Title = styled.span`
    display: inline-block;
    font-family: rubik-light;
    width: 2.5rem;
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    cursor: default;
    color: hsl(0deg, 0%, 75%);
`

// the controller housing
const Housing = styled(SVG)`
    margin: 0.25rem auto;
    border: 1px solid hsl(0deg, 0%, 10%);
`

// the controller
const Controller = styled(Range)`
`


// end of file
