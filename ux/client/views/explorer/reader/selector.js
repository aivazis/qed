// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useViews } from '../explorer/useViews'
// styles
import { selector as paintSelector } from './styles'


// the decorator of a {dataset} tab
export const Selector = ({ viewport, view }) => {
    // get the active view
    const { activeViewport } = useViews()

    // unpack the view
    const { dataset } = view
    // get the dataset uri
    const uri = dataset?.uri ?? ""

    // deduce my state
    const state = (viewport === activeViewport) ? "selected" : "enabled"
    // mix my paint
    const paint = paintSelector(state)
    // and render
    return (
        <span style={paint.box}>
            {/* the archive name */}
            <span style={paint.name}>connect dataset</span>
            {/* a separator */}
            <span style={paint.separator}>&middot;</span>
            {/* the dataset uri */}
            <span style={paint.selector}>{uri}</span>
        </span>
    )
}


// end of file