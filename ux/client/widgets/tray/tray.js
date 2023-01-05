// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// theme
import { theme } from '~/palette'

// locals
// components
import { Indicator } from './indicator'


// a tray with a header and some items
export const Tray = ({ title, state, initially = false, children }) => {
    // storage for my state
    const [expanded, setExpanded] = React.useState(initially)
    // handler for flipping my state
    const toggle = () => setExpanded(!expanded)

    // pick my parts based on my state
    const { Header, Title } = components(state)

    // paint me
    return (
        <Section>
            <Header onClick={toggle}>
                <Indicator expanded={expanded} />
                <Title>{title}</Title>
            </Header>
            {expanded && <Items>{children}</Items>}
        </Section>
    )
}


// state dependent selection
const components = state => {
    // when i'm selected
    if (state === "selected") {
        return { Header: SelectedHeader, Title: SelectedTitle }
    }

    // otherwise
    return { Header, Title }
}


// parts
// the box
const Section = styled.section`
    /* for me */
    /* i neither stretch nor shrink*/
    flex: 0 0 auto;
    min-height: 1.3rem;
    /* for my children */
    display: flex;
    flex-direction: column;
    overflow: hidden;
`


// the header
const Header = styled.div`
    /* style */
    font-size: 60%;
    padding: 0.25rem 0.0rem 0.25rem 0.6rem;
    cursor: pointer;
    /* colors */
    color: hsl(0deg, 0%, 60%, 1);
    background-color: hsl(0deg, 0%, 12%, 1);
    /* don't stretch me */
    flex: 0;

    /* for my children */
    display: flex;
    align-items: center;
`

const SelectedHeader = styled(Header)`
    background-color: hsl(0deg, 0%, 17%, 1);
`


// the title
const Title = styled.span`
    /* style */
    font-family: rubik-medium;
    padding: 0.0rem 0.0rem 0.0rem 0.5rem;
    /* disable text selection */
    user-select: none;
`

const SelectedTitle = styled(Title)`
    color: ${theme.page.name};
`


// the items
const Items = styled.div`
    /* i stretch but don't shrink*/
    flex: 1 0 auto;
    /* gimme some room */
    padding: 0.25rem 0.0rem;
    /* for my children */
    display: flex;
    flex-direction: column;
    overflow: auto;
`


// end of file
