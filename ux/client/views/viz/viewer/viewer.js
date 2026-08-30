// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// locals
// components
import { Blank } from './blank'
import { Info } from './info'
import { Preparing } from './preparing'
import { Tab } from './tab'
import { Viewport } from './viewport'


// export the data viewer
export const Viewer = ({ viewport, view, registrar }) => {
    // unpack the view
    const { ready, preparing } = useFragment(viewerGetViewFragment, view)
    // a dataset that has been chosen but not yet prepared would render badly: no pyramid,
    // so a zoomed out view strides the whole product, and a display range guessed from a
    // handful of windows rather than measured over everything. wait for the pass instead
    if (preparing) {
        // the tab is handed nothing, exactly as it is when the viewport is blank: the
        // controls it offers all read through a channel, and a dataset that has only just
        // been chosen has none yet
        return (
            <>
                <Tab viewport={viewport} view={null} />
                <Preparing />
            </>
        )
    }
    // the server settles what a render requires, so ask it rather than inferring
    // readiness from the nullable joins it settled it from
    if (!ready) {
        // to show a blank panel
        return (
            <>
                <Tab viewport={viewport} view={null} />
                <Blank />
            </>
        )
    }
    // otherwise, render
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


// my fragment
const viewerGetViewFragment = graphql`
    fragment viewerGetViewFragment on View {
        id
        # whether everything a tile request needs has been settled, as computed by the
        # server; it is the only gate this component consults
        ready
        # and whether the work that makes the dataset worth looking at is still running
        preparing
    }
`


// end of file
