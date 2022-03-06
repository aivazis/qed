// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// a widget that contains a lazily loaded image
export const Tile = ({ uri, shape }) => {
    // render
    return (
        <Image shape={shape} loading="lazy" className="lazyload" data-src={uri} />
    )
}


// the contents
const Image = styled.img`
    /* i'm not resizable; my parent uses flex to position me */
    flex: none;
    /* extent */
    width: ${props => props.shape[1]}px;
    height: ${props => props.shape[0]}px;
`


// end of file
