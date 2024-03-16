// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Spacer } from '~/widgets'
// colors
import { theme } from '~/palette'

// locals
// components
import { Indicator } from './indicator'


// a tray with a header and some items
export const Tray = ({
    style,
    title, state, initially = false, scale = 1.0, busy = false, controls = null,
    children
}) => {
    // scale up a bit on large displays
    const rem = (window.screen.width > 2048 ? 1.2 : 1.0) * scale
    // convert to pixels
    const size = rem * parseFloat(getComputedStyle(document.documentElement).fontSize)

    // storage for my state
    const [expanded, setExpanded] = React.useState(initially)
    // handler for flipping my state
    const toggle = () => setExpanded(!expanded)

    // pick my parts based on my state
    const { Header, Title } = components(state)

    // mix my paint
    const paint = {
        // set the font size
        '--font-size': `${size}px`,
        // plus whatever the user said
        ...style,
    }

    // paint me
    return (
        <Section style={paint}>
            <Header style={paint} onClick={toggle}>
                <Indicator expanded={expanded} size={0.6 * size} />
                <Title>{title}</Title>
                <Spacer />
                {busy && <Busy />}
                {controls}
            </Header>
            {expanded && <Items style={paint}>{children}</Items>}
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
export const Section = styled.section`
    /* sizing */
    font-size: var(--font-size);
    font-family: inconsolata;

    /* for me */
    /* i neither stretch nor shrink*/
    flex: 0 0 auto;

    /* for my children */
    display: flex;
    flex-direction: column;
    overflow: hidden;
`

// the header
export const Header = styled.div`
    /* style */
    padding: 0.25rem 0.5rem 0.25rem 0.5rem;
    cursor: pointer;
    /* colors */
    color: var(--header-color, ${() => theme.page.bright});
    background-color: var(--header-background, ${() => theme.page.relief});
    /* don't stretch me */
    flex: 0;

    /* for my children */
    display: flex;
    align-items: center;
`

export const SelectedHeader = styled(Header)`
    background-color: var(--header-selected, ${() => theme.page.active});
`

// the title
export const Title = styled.span`
    /* style */
    font-family: rubik-medium;
    padding-left: 0.5em;
    /* disable text selection */
    user-select: none;
`

export const SelectedTitle = styled(Title)`
    color: ${() => theme.page.name};
`

// the busy indicator
export const Busy = styled.div`
    width: 1.0em;
    height: 1.0em;
    border: 3px solid ${() => theme.page.normal};
    border-radius: 50%;
    border-top: 3px solid ${() => theme.page.normal};
    animation: busy 1s linear infinite;
`

// the items
export const Items = styled.div`
    /* i stretch but don't shrink */
    flex: 1 0 auto;
    /* gimme some room */
    padding-left: var(--indent, 0em);
    padding-top: 0.5em;
    padding-bottom: 0.5em;
    /* for my children */
    display: flex;
    flex-direction: column;
    overflow: auto;
`


// end of file
