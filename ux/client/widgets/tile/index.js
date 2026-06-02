// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'


// a widget that contains a lazily loaded image; a tile is one slice of a larger {mosaic}
// image, so it carries an empty {alt} by default and reads as decorative to assistive tech
export const Tile = ({ uri, shape, alt = "", ...rest }) => {
    // render
    return (
        <Image shape={shape} loading="lazy" className="lazyload" data-src={uri}
            alt={alt} data-pyre-widget="tile" {...rest} />
    )
}


// the contents
const Image = styled.img`
    /* i'm not resizable; my parent uses flex to position me */
    flex: none;
    /* extent */
    width: ${props => props.shape[1]}px;
    height: ${props => props.shape[0]}px;
    /* when zooming */
    image-rendering: pixelated;
`


// end of file
