// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// the sync control table header
export const Header = () => {
    // render
    return (
        <Head>
            <Title>
                <Column></Column>
                <Column>channel</Column>
                <Column>zoom</Column>
                <Column>scroll</Column>
                <Column>path</Column>
                <Column>offsets</Column>
            </Title>
        </Head>
    )
}


// headers
const Head = styled.thead`
`

const Title = styled.tr`
`

const Column = styled.th`
    font-family: rubik-light;
    font-weight: normal;
    text-align: center;
    vertical-align: middle;
    padding: 0.5em 0.0em ;
    cursor: default;
`


// end of file