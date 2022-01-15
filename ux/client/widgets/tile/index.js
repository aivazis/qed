// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// a widget that can act as a header or a title
export const Tile = ({ uri, style, ...rest }) => {
    // mix my paint
    const tileStyle = { ...styles, ...style }

    // render
    return (
        <img loading="lazy" className="lazyload" data-src={uri} style={tileStyle} {...rest} />
    )
}


// end of file
