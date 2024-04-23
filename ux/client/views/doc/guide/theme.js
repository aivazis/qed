// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// external
import styled from 'styled-components'

// project
import { theme } from '~/palette'


export const Title = styled.h1`
    font-size: large;
    font-weight: 400;
    margin: 1.0rem;
    padding: 0.5rem;
    color: ${props => theme.page.highlight};
    background-color: ${props => theme.page.active};
`

export const Section = styled.h2`
    font-size: large;
    font-weight: 300;
    margin: 1.0rem;
    padding: 0.5rem;
    color: ${props => theme.page.highlight};
    background-color: ${props => theme.page.relief};
`

export const Subsection = styled.h3`
    font-size: medium;
    font-weight: 300;
    margin: 1.0rem;
    padding: 0.5rem;
    color: ${props => theme.page.highlight};
    background-color: ${props => theme.page.relief};
`

export const Text = styled.p`
    font-size: medium;
    font-weight: 200;
    line-height: 150%;
    margin: 0.0rem 0.675rem;
    padding: 0.5rem;
    color: ${props => theme.page.bright};
`


// end of file