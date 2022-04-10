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
import { Range } from '~/widgets'


// a ranged controller
export const RangeController = props => {
    // unpack the data
    const configuration = useFragment(graphql`
        fragment range_range on RangeController {
            id
            slot
            min
            max
            low
            high
        }
    `, props.configuration)

    // show me
    console.log(configuration)

    // all done
    return null
}


// end of file
