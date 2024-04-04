// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// local
// components
import { Add } from './add'
import { Close } from './close'
import { Coordinate } from './coordinate'
import { Delete } from './delete'
import { Focus } from './focus'


// an entry from the table of the points on the {measure} layer of the active viewport
export const Point = ({ viewport, view, idx, point, last }) => {
    // draw an entry of the {path} table
    return (
        <Box>
            {/* select this point*/}
            <Focus viewport={viewport} view={view} idx={idx} point={point} />

            {/* coordinates */}
            {<Coordinate viewport={viewport} view={view} node={idx} axis={"y"} point={point} />}
            {<Coordinate viewport={viewport} view={view} node={idx} axis={"x"} point={point} />}

            {/* delete this point */}
            {<Delete viewport={viewport} idx={idx} />}
            {/* place the control that adds a point after this one, unless its the last one */}
            {idx != last && <Add viewport={viewport} idx={idx} />}
            {/* instead, the last point gets a control to close the path */}
            {idx == last && <Close viewport={viewport} view={view} />}
        </Box>
    )
}


// the container
const Box = styled.div`
    display: flex;
    align-items: end;
    font-family: inconsolata;
    height: 1.2em;
    margin: 0em;
    padding: 0.125rem 0.0rem;
`


// end of file
