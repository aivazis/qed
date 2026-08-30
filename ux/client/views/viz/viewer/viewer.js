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
    const { ready, preparing, reader, dataset, channel } = useFragment(
        viewerGetViewFragment, view)
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
    // the server settles what a render requires, so ask it rather than deciding for
    // ourselves what readiness means. the three joins are checked too, and deliberately:
    // {ready} is computed from them, but it travels in its own field, and a payload that
    // clears one of them without carrying the flag would leave a stale {ready} standing
    // for a render -- long enough for what follows to dereference a null. the flag says
    // what the server means; the joins say what this component may safely touch
    if (!ready || !reader || !dataset || !channel) {
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
        # server, which is the authority on what a render requires
        ready
        # and whether the work that makes the dataset worth looking at is still running
        preparing
        # the joins the components below dereference; carried so this component can refuse
        # to render onto a null even if {ready} has not caught up yet
        reader {
            id
        }
        dataset {
            id
        }
        channel {
            id
        }
    }
`


// end of file
