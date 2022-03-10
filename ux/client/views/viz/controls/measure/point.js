// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// local
// components
import { Add } from './add'
import { Coordinate } from './coordinate'
import { Delete } from './delete'
import { Focus } from './focus'


// a line in the table of the points on the {measure} layer of the active viewport
export const Point = ({ idx, point, last }) => {
    // draw a line of the {path} table
    return (
        <Box>
            <Index>{idx}:</Index>
            <Coordinate node={idx} axis={0} point={point} />
            <Coordinate node={idx} axis={1} point={point} />

            {/* select this point*/}
            <Focus idx={idx} point={point} />
            {/* delete this point */}
            <Delete idx={idx} />
            {/* add a point after this one, unless its the last */}
            {idx != last && <Add idx={idx} />}

        </Box>
    )
}


// the container
const Box = styled.div`
    font-family: inconsolata;
    font-size: 75%;
    padding: 0.2rem 0.0rem;
`

const Index = styled.span`
    display: inline-block;
    width: 2.0rem;
    text-align: end;
`


// end of file
