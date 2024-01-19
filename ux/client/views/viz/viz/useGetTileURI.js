// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// local
// context
import { Context } from './context'


// hook to pull the dataset readers out the outlet context
export const useGetTileURI = ({ viewport, zoomLevel }) => {
    // grab some stuff from my context
    const { activeViewport, views, zoom } = React.useContext(Context)
    // normalize the viewport
    viewport ??= activeViewport
    // get the viewport zoom setting
    const viewportZoom = zoom[viewport]
    // and the zoom level
    zoomLevel ??= viewportZoom
    // project
    const level = [Math.trunc(zoomLevel.vertical), Math.trunc(zoomLevel.horizontal)].join("x")

    // get the view
    const view = views[viewport]
    // unpack it
    const { reader, dataset, channel } = view

    // check for the trivial cases
    if (!reader || !dataset || !channel) {
        // bail
        return null
    }

    // otherwise, unpack
    const { api } = reader
    const { name } = dataset

    // assemble the base data request URI
    const uri = [api, name, channel, level].join("/")

    // and return it
    return uri
}


// end of file
