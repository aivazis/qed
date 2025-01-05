// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
// paint
import { theme } from '~/palette'


// a container of shapes
export const Badge = ({ size = 12, children }) => {
    // size the shape
    const shrink = `scale(${size / 1000})`
    // render
    return (
        <Housing>
            <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width={size} height={size} >
                <g transform={shrink} >
                    {children}
                </g>
            </svg>
        </Housing>
    )
}


// the housing
const Housing = styled.span`
    padding: 0.0em 0.5em 0.0em 0.5em;
    background-color: ${props => theme.page.active};
`


// end of file
