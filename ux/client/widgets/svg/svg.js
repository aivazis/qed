// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// export the SVG wrapper
export const SVG = ({ height, width, children, ...rest }) => {
    // and render
    return (
        <Container
            height={height} width={width} {...rest}
            version="2.0" xmlns="http://www.w3.org/2000/svg"
        >
            {children}
        </Container>
    )
}


// styling
const Container = styled.svg``


// end of file
