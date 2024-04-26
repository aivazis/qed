// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// external
import styled from 'styled-components'

// project
import { theme } from '~/palette'


export const Title = styled.h1`
    font-size: xx-large;
    font-weight: 400;
    margin: 1.5rem 0.0rem 0.0rem 0.0rem;
    padding: 0.5rem 0.5rem 0.5rem 0.5rem;
    color: ${props => theme.page.highlight};
    background-color: ${props => theme.page.relief};
`

export const Section = styled.h2`
    font-size: x-large;
    font-weight: 300;
    margin: 1.5rem 0.0rem 0.0rem 0.0rem;
    padding: 0.5rem 0.5rem 0.5rem 0.5rem;
    color: ${props => theme.page.highlight};
    background-color: ${props => theme.page.relief};
`

export const Subsection = styled.h3`
    font-size: large;
    font-weight: 300;
    margin: 1.5rem 0.0rem 0.0rem 0.0rem;
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

export const Bold = styled.strong`
    font-weight: 300;
    color: ${props => theme.page.highlight};
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
