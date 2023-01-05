// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// components
import { Blank } from './blank'
import { Info } from './info'
import { Tab } from './tab'
import { Viewport } from './viewport'


// export the data viewer
export const Viewer = ({ viewport, view, registrar }) => {
    // unpack the view
    const { reader, dataset, channel } = view
    // check for the trivial cases
    if (!reader || !dataset || !channel) {
        // to show a blank panel
        return (
            <>
                <Tab viewport={viewport} view={null} />
                <Blank />
            </>
        )
    }

    // otherwise,  render
    return (
        <>
            {/* the title bar with the dataset description and the controls */}
            <Tab viewport={viewport} view={view} />
            {/* identifying metadata; most of it is debugging information */}
            <Info viewport={viewport} view={view} />

            {/* the viewport */}
            <Viewport viewport={viewport} view={view} registrar={registrar} />
        </>
    )
}


// end of file
