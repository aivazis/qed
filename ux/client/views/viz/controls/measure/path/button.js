// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { SVG } from '~/widgets'


// a line in the table of the points on the {measure} layer of the active viewport
export const Button = ({ size = 12, behaviors, children, ...rest }) => {
    // make a mark
    return (
        <Mark {...rest}>
            <Icon {...behaviors}>
                <g transform={`scale(${size / 1000})`} >
                    {children}
                </g>
            </Icon>
        </Mark>

    )
}


const Mark = styled.div`
    width: 2.0rem;
    text-align: end;
`

const Icon = styled(SVG)`
    width: 0.7rem;
    height: 0.7rem;
    vertical-align: bottom;
    cursor: pointer;
`


// end of file
