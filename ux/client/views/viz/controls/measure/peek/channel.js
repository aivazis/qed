// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


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


// theo cntainer
const Entry = styled.div`
    font-size: 60%;
`

const Label = styled.span`
    display: inline-block;
    font-family: rubik-light;
    width: 4.0rem;
    text-align: end;
    text-transform: uppercase;
    padding: 0.0rem 0.0rem 0.25rem 0.0rem;
    margin: 0.0rem 0.0rem 0.1rem 0.0rem;
`

const Value = styled.span`
    display: inline-block;
    font-family: inconsolata;
    cursor: default;
    width: 3.25rem;
    text-align: end;
    padding: 0.0rem;
    overflow: clip;
    padding: 0.0rem 0.0rem 0.0rem 0.5rem;
`

// the state control
const Button = styled.button`
    & {
        cursor: pointer;
        font-family: rubik-light;
        text-align: start;
        color: inherit;
        background-color: transparent;
        border: 0 transparent;
        margin: 0.0rem;
        padding: 0.0rem 0.0rem 0.0rem 0.5rem;
    }

    &:active {
        color: hsl(28deg, 90%, 55%);
        border: 1 solid hsl(0deg, 0%, 40%);
    }

    &:hover {
        color: hsl(28deg, 90%, 55%);
        border: 1 solid hsl(0deg, 0%, 40%);
    }
`


// end of file
