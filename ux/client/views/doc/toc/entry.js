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
export const Entry = ({ entry }) => {
    // render
    return (
        <Link to={`${entry.link}`}>
            <Title>
                {entry.title}
            </Title>
        </Link>
    )

}

// the parts
const Title = styled.div`
    & {
        padding: 0.5em 0.0em 0.5em 1.0rem;
        cursor: pointer;
    }

    &:hover {
        color: ${props => theme.page.highlight};
    }
`


// end of file
