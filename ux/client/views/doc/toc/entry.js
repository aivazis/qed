// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'
import { Link } from 'react-router-dom'

// project
// hooks
import { useTopic } from '~/views'
// paint
import { theme } from '~/palette'


// a TOC entry
export const Entry = ({ entry }) => {
    // get the topic and its selector
    const { topic, pick } = useTopic()
    // if the location ends with my link, i'm the current topic
    const current = entry.link === topic
    // pick the component to render
    const Title = current ? Current : Topic

    // set up my behaviors
    const behaviors = {
        // do nothing when current, otherwise pick my topic
        onClick: current ? null : () => pick(entry.link),
    }

    // render
    return (
        <Section>
            <Title {...behaviors}>
                {entry.title}
            </Title>
            {current && entry.contents?.map(item => {
                // render
                return (
                    <Subsection key={item.link} href={item.link}>
                        {item.title}
                    </Subsection>
                )
            })}
        </Section>
    )

}

// the parts
const Section = styled.nav`
`

const Topic = styled.div`
    & {
        padding: 0.5em 0.0em 0.5em 1.0rem;
        cursor: pointer;
    }

    &:hover {
        color: ${props => theme.page.highlight};
    }
`

const Current = styled.div`
    padding: 0.5em 0.0em 0.5em 1.0rem;
    color: ${props => theme.page.highlight};
    cursor: default;
`

const Subsection = styled.a`
    & {
        display: block;
        font-size: small;
        padding: 0.5em 0.0em 0.5em 2.0rem;
        cursor: pointer;
    }

    &:hover {
        color: ${props => theme.page.highlight};
    }
`


// end of file
