// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useViews } from './useViews'
// styles
import { selector as paintSelector } from './styles'


// remove a {viewport} from the {viz} panel
export const Selector = ({ viewport, view }) => {
    // get the active view
    const { activeViewport } = useViews()

    // unpack the view
    const { archive, dataset } = view
    // get the name of the data archive
    const archiveName = archive.name
    // the name of the dataset
    const datasetName = dataset?.name

    // deduce my state
    const state = (viewport === activeViewport) ? "selected" : "enabled"
    // mix my paint
    const paint = paintSelector(state)
    // and render
    return (
        <span style={paint.box}>
            {/* the archive name */}
            {archiveName && <span style={paint.name}>{archiveName}</span>}
            {/* a separator */}
            {archiveName && <span style={paint.separator}>&middot;</span>}
            {/* the dataset name */}
            {datasetName && <span style={paint.selector}>{tableName}</span>}
        </span>
    )
}


// end of file