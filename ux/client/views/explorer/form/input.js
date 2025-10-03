// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import styled from 'styled-components'

// project
// theme
import { theme } from '~/palette'


// the base input
export const Input = styled.input`
    display: inline-block;
    font-size: 100%;
    appearance: textfield;
    outline: none;
    cursor: pointer;
    font-family: inconsolata;
    width: 20.0rem;
    text-align: start;
    padding: 0.0rem 0.25rem 0.0rem 0.0rem;
    border: 0 transparent;
`

export const EnabledInput = styled(Input)`
    & {
        color: hsl(0deg, 0%, 60%);
        background-color: ${theme.widgets.background};
    }

    &:hover {
        color: hsl(28deg, 90%, 55%);
    }

    &:active{
        color: hsl(28deg, 90%, 55%);
    }

    &:focus{
        color: ${theme.widgets.focus.color};
        background-color: ${theme.widgets.focus.background};
    }

    &:invalid {
        color: hsl(0deg, 50%, 50%);
    }

    &::selection {
        background-color: ${theme.widgets.selection.color};
        background-color: ${theme.widgets.selection.background};
    }
`

export const SelectedInput = styled(Input)`
    color: hsl(28deg, 90%, 55%);
`

export const Numeric = styled(EnabledInput)`
    width: 6em;
    text-align: end;
`

// end of file
