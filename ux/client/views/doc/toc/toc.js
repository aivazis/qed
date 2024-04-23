// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// external
import React from 'react'
import styled from 'styled-components'

// project
import { theme } from '~/palette'

//  local
import { topics } from '../contents'
import { Entry } from './entry'


// the table of contents
export const TOC = () => {
    // render
    return (
        <Section>
            <Title>Contents</Title>
            <Contents>
                {topics.map(entry => <Entry key={entry.link} entry={entry} />)}
            </Contents>
        </Section>
    )
}


// the parts
const Section = styled.nav`
    font-family: rubik-light;
    font-size: medium;
    color: ${props => theme.page.normal}
`

const Title = styled.h3`
    padding: 1.0rem 0.0rem 1.0rem 1.0rem;
    color: ${props => theme.page.bright};
    background-color: ${props => theme.page.background};
`

const Contents = styled.div`
    display: flex;
    flex-direction: column;
`

// end of file
