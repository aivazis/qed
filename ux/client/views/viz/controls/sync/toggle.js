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


//  a toggle
export const Toggle = ({ size, state, toggle }) => {
    // set up my behaviors
    const behaviors = {
        onClick: toggle,
    }
    // mix my paint
    const Button = state ? SelectedButton : ActiveButton;
    // and render
    return (
        <Housing width={size + 4} height={size + 4}>
            <g transform={`translate(${size / 2 + 2} ${size / 2 + 2}) scale(${size / 2})`}>
                <Button cx={0} cy={0} r={1} {...behaviors} />
            </g>
        </Housing>
    )
}

//            </g>
//            <g transform={`translate(${ size / 2} ${ size / 2}) scale(${ size })`}>


// the housing
const Housing = styled(SVG)`
`

// the  button
const ActiveButton = styled.circle`
    fill: none;

    stroke: hsl(0deg, 0%, 40%);
    stroke-width: 1;
    vector-effect: non-scaling-stroke;

    cursor: pointer;
`

const SelectedButton = styled.circle`
    fill: hsl(28deg, 90%, 45%);
    cursor: pointer;
`


// end of file
