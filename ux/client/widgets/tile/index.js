// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// locals
import { watch } from './loader'


// a widget that contains a lazily loaded image; a tile is one slice of a larger {mosaic}
// image, so it carries an empty {alt} by default and reads as decorative to assistive tech
export const Tile = ({ uri, shape, alt = "", ...rest }) => {
    // a handle to the image
    const image = React.useRef(null)
    // hand the image to the loader whenever its address changes, so the new one is fetched once
    // the tile is within reach, and take it back when the tile goes away
    React.useEffect(() => watch(image.current), [uri])
    // render
    return (
        <Image ref={image} shape={shape} data-src={uri}
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
