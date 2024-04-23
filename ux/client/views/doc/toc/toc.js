// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

// external
import React from 'react'
import styled from 'styled-components'
import { useLocation } from 'react-router-dom'

// project
import { theme } from '~/palette'

//  local
import { Entry } from './entry'


// the table of contents
export const TOC = () => {
    // get the location
    const location = useLocation()
    // and extract the path
    const here = location.pathname
    // render
    return (
        <Section>
            <Title>Contents</Title>
            <Contents>
                {toc.map(entry => <Entry key={entry.link} here={here} entry={entry} />)}
            </Contents>
        </Section>
    )
}

// the table of contents
const toc = [
    { title: "Getting started", link: "intro" },
    { title: "Connecting to data archives", link: "archives" },
    { title: "Loading datasets", link: "readers" },
    { title: "Selecting datasets", link: "datasets" },
    { title: "Adjusting the view", link: "views" },
    { title: "The measure layer", link: "measure" },
    { title: "Working with multiple data panels", link: "panels" },
]


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
