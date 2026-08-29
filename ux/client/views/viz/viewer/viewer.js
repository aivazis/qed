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
import { Tab } from './tab'
import { Viewport } from './viewport'


// export the data viewer
export const Viewer = ({ viewport, view, registrar }) => {
    // unpack the view
    const { ready } = useFragment(viewerGetViewFragment, view)
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
    }
`


// end of file
