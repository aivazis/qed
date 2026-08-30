// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// the panel shown while a dataset is being made worth looking at
// selecting a dataset settles what to render; it does not settle how well. the pyramid that
// makes a zoomed out view cheap, the display range measured over the whole raster rather
// than guessed from a corner, and the thumbnail that reads a level rather than the product
// all come from one pass over the data, and this is what stands in until it lands
export const Preparing = ({ behaviors }) => {
    // render
    return (
        <Panel data-qed-viewport-status="preparing" {...behaviors}>
            <Ring />
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

// the spinner
const Ring = styled.div`
    width: 90px;
    height: 90px;
    border: 3px solid hsl(28deg, 90%, 55%);
    border-radius: 50%;
    border-top: 3px solid hsl(28deg, 90%, 55%, 0.25);
    animation: busy 1s linear infinite;
`

// and what it is waiting for
const Note = styled.span`
    font-size: 70%;
    letter-spacing: 0.1rem;
    color: hsl(0deg, 0%, 55%);
`


// end of file
