// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Spinner } from '~/widgets'


// the panel shown while a dataset is being made worth looking at
// selecting a dataset settles what to render; it does not settle how well. the pyramid that
// makes a zoomed out view cheap, the display range measured over the whole raster rather
// than guessed from a corner, and the thumbnail that reads a level rather than the product
// all come from one pass over the data, and this is what stands in until it lands
export const Preparing = ({ behaviors }) => {
    // render
    return (
        <Panel data-qed-viewport-status="preparing" {...behaviors}>
            <Spinner size="90px" />
            <Note>preparing the dataset...</Note>
        </Panel>
    )
}


// the panel fills the viewport, the way the blank placeholder does
const Panel = styled.section`
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
`

// and what it is waiting for
const Note = styled.span`
    font-size: 70%;
    letter-spacing: 0.1rem;
    color: hsl(0deg, 0%, 55%);
`


// end of file
