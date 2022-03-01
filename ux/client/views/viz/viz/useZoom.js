// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// access to the zoom level and its mutator
export const useZoom = () => {
    // grab the zoom level and its mutator
    const { activeViewport, zoom, setZoom } = React.useContext(Context)
    // and publish
    return { activeViewport, zoom, setZoom }
}


// end of file
