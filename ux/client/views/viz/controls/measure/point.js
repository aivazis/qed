// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// shapes
import { Plus, Target, X } from '~/shapes'

// local
// components
import { Button } from './button'


// the point selector
const Potato = styled(Button)`
    background-color: blue;
    border-bottom: 1px solid blue;
`



// a line in the table of the points on the {measure} layer of the active viewport
export const Point = ({ idx, point }) => {
    // make a mark
    return (
        <Box>
            <Index>{idx}:</Index>
            <Coordinate>{point[1]}</Coordinate>
            <Coordinate>{point[0]}</Coordinate>

            {/* select this point*/}
            <Button>
                <Target />
            </Button>
            {/* add a point after this one */}
            <Button>
                <Plus />
            </Button>
            {/* delete this point */}
            <Button>
                <X />
            </Button>

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

const Coordinate = styled.span`
    display: inline-block;
    width: 2.75rem;
    text-align: end;
    padding: 0.0rem 0.25rem 0.0rem 0.0rem;
`

// end of file
