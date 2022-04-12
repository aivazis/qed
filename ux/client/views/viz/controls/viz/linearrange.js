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


// a ranged controller
export const LinearRangeController = props => {
    // unpack the data
    const configuration = useFragment(graphql`
        fragment linearrange_linearrange on LinearRangeController {
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

    // set up the tick marks
    const major = [min, min / 2, 0, max / 2, max]

    // the value updated
    const setValue = v => console.log(v)
    // controller configuration
    const range = {
        value: [low, high], setValue,
        min, max, major,
        direction: "row", labels: "bottom", arrows: "top",
        height: 100, width: 250,
    }

    // show me
    console.log(range)

    // render
    return (
        <>
            <Header>
                <Title>{slot}</Title>
            </Header>
            <Housing height={range.height} width={range.width}>
                <Controller enabled={true} {...range} />
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
