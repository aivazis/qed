// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { SVG } from '~/widgets'


// a line in the table of the points on the {measure} layer of the active viewport
export const Button = ({ children, ...rest }) => {
    // make a mark
    return (
        <Mark {...rest}>
            <Icon>
                <g transform={`scale(${14 / 1000})`} >
                    {children}
                </g>
            </Icon>
        </Mark>

    )
}


const Mark = styled.span`
    display: inline-block;
    width: 2.0rem;
    text-align: end;
`

const Icon = styled(SVG)`
    width: 0.7rem;
    height: 0.7rem;
    vertical-align: bottom;
`


// end of file
