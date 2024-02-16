// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import styled from 'styled-components'


// the dataset preview
export const Preview = ({ reader, uri, lines, samples, cell = "" }) => {
    // compute the scaling factor to bring the width of the image down to around 512 pixels
    const scale = Math.max(samples, lines) / 512
    // convert this into a zoom level
    const zoom = Math.trunc(Math.log2(scale))
    // compute the new width
    const width = Math.trunc(samples / (2 ** zoom))
    // and the new height
    const height = Math.trunc(lines / (2 ** zoom))

    // form the api
    const api = `preview?reader=${reader}&uri=${uri}&cell=${cell}`
    // build the uri
    const request = `${api}&shape=${lines},${samples}&zoom=${zoom}&view=${height},${width}`
    // render
    return (
        <Viewport src={request} width={width} height={height} />
    )
}


// the viewport
const Viewport = styled.img`
    display: block;
    margin: 2.0em auto;
`

// end of file