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
    padding: 0.5rem 0.5rem 0.5rem 0.5rem;
    color: ${props => theme.page.highlight};
    background-color: ${props => theme.page.active};
`

export const Section = styled.h2`
    font-size: medium;
    font-weight: 300;
    padding: 0.5rem 0.5rem 0.5rem 0.5rem;
    color: ${props => theme.page.highlight};
    background-color: ${props => theme.page.relief};
`

export const Subsection = styled.h3`
    font-size: medium;
    font-weight: 300;
    padding: 0.5rem 0.5rem 0.5rem 0.5rem;
    color: ${props => theme.page.highlight};
    background-color: ${props => theme.page.relief};
`

export const Text = styled.p`
    font-size: medium;
    font-weight: 200;
    line-height: 150%;
    padding: 0.5rem 0.5rem 0.5rem 0.5rem;
    color: ${props => theme.page.bright};
`


export const Link = styled.a`
    & {
        color: ${props => theme.page.link};
    }

    &:link {
        color: ${props => theme.page.link};
    }

    &:hover {
        color: ${props => theme.page.linkActive};
    }

    &:active {
        color: ${props => theme.page.linkActive};
    }

    &:visited {
        color: ${props => theme.page.link};
    }
`


// end of file
