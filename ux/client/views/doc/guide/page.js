// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'

// project
import { theme } from '~/palette'

// a page
export const Page = ({ children }) => {
    // render
    return (
        <Section>
            <Box>
                {children}
            </Box>
        </Section>

    )
}


// the content wrapper
const Section = styled.section`
    font-family: rubik-light;
    font-size: small;
    color: ${props => theme.page.bright};
    overflow: auto;
`

const Box = styled.div`
    width: 60.0em;
`

// end of file
