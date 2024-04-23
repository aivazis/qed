// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'
import { Link } from 'react-router-dom'

// project
import { theme } from '~/palette'


// a TOC entry
export const Entry = ({ here, entry }) => {
    // if the location ends with my link, i'm the current topic
    const current = here.endsWith(entry.link)
    // pick the component to render
    const Text = current ? Current : Topic

    // render
    return (
        <Link to={`${entry.link}`}>
            <Text>
                {entry.title}
            </Text>
        </Link>
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
