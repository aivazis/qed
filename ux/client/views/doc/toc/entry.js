// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


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
    const Text = current ? Current : Topic

    // set up my behaviors
    const behaviors = {
        // do nothing when current, otherwise pick my topic
        onClick: current ? null : () => pick(entry),
    }

    // render
    return (
        <Text {...behaviors}>
            {entry.title}
        </Text>
    )

}

// the parts
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


// end of file
