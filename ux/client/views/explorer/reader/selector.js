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


// the decorator of a {reader} tab
export const Selector = ({ viewport, view }) => {
    // get the active view
    const { activeViewport } = useViews()

    // unpack the view
    const { reader } = view
    // get the reader uri
    const uri = reader?.uri ?? ""

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
            {/* the reader uri */}
            <span style={paint.selector}>{uri}</span>
        </span>
    )
}


// end of file