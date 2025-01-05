// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// colors
import { theme } from "~/palette"


// display the channel specific representation of a pixel value
export const Channel = ({ channel, reps }) => {
    // support for cycling through the possible value representations
    const [choice, setChoice] = React.useState(0)

    // find out how many options there are
    const choices = reps.length
    // unpack the current one
    const { rep, units } = reps[choice]

    // make handler that cycles through the choices
    const cycle = () => setChoice(old => (old + 1) % choices)

    // render
    return (
        <Entry key={channel}>
            <Label>{channel} :</Label>
            <Value>{rep}</Value>
            {units && <Button onClick={cycle}>{units}</Button>}
        </Entry>
    )
}


// the container
const Entry = styled.div`
    display: flex;
    align-items: end;
    height: 1.2em;
    margin: 0.0rm;
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    color: ${() => theme.page.normal};
`

const Label = styled.div`
    font-family: rubik-light;
    width: 4.0rem;
    text-align: end;
    text-transform: uppercase;
    cursor: default;
`

const Value = styled.div`
    font-family: inconsolata;
    font-size: 110%;
    width: 6.0rem;
    text-align: end;
    overflow: clip;
    cursor: default;
`

// the state control
const Button = styled.div`
    & {
        cursor: pointer;
        font-family: rubik-light;
        text-align: start;
        margin: 0.0rem;
        padding: 0.0rem 0.0rem 0.0rem 0.5rem;
    }

    &:active {
        color: ${() => theme.page.highlight};
        border: 1 solid ${() => theme.page.normal};
    }

    &:hover {
        color: ${() => theme.page.highlight};
        border: 1 solid ${() => theme.page.normal};
    }
`


// end of file
