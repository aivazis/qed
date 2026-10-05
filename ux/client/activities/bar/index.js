// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

// locals
// the activities
import { About, Console, Controls, Data, Explore, Flow, Help, Kill, Quality } from '~/activities'
// widgets
import { Toolbar, Spacer } from '~/widgets'
// the state of the viewports
import { useViewports } from '~/views/viz'
// styles
import styles from './styles'


// the activity bar
export const Bar = ({ qed, style }) => {
    // the views, and the active viewport
    const { views } = useFragment(activityBarGetViewsFragment, qed)
    const { activeViewport } = useViewports()
    // the active view
    const view = views[activeViewport]
    // the activities that work on its data make no sense without a dataset
    const empty = !view?.dataset
    // and the ones that work on its pipeline need a channel as well
    const unpiped = empty || !view?.channel
    // pick an icon size based in the screen resolution
    const rem = window.screen.width > 2048 ? 1.2 : 1.0
    // convert to pixels
    const size = rem * parseFloat(getComputedStyle(document.documentElement).fontSize)

    // mix my paint
    const paint = styles.bar(style)
    // paint me
    return (
        <Toolbar direction="column" style={paint} >
            <Explore size={size} style={paint} />
            <Data size={size} style={paint} />
            <Controls size={size} disabled={unpiped} style={paint} />
            <Flow size={size} disabled={unpiped} style={paint} />
            <Quality size={size} disabled={empty} style={paint} />
            <Console size={size} style={paint} />
            <Help size={size} style={paint} />

            <Spacer />

            {/* disable, for now: it is unrecoverable on NISAR the on-demand system */}
            <Kill size={size} style={paint} />
            <About size={size} style={paint} />
        </Toolbar>
    )
}


// my fragment
const activityBarGetViewsFragment = graphql`
    fragment activityBarGetViewsFragment on QED {
        views {
            # whether there is a dataset in the view
            dataset {
                name
            }
            # and a channel to render it with
            channel {
                tag
            }
        }
    }
`


// end of file
