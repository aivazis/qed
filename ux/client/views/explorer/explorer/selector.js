// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// components
import { Selector as Archive } from '../archive'
import { Selector as Dataset } from '../dataset'


// the decorator of a {dataset} tab
export const Selector = ({ viewport, view }) => {
    // unpack the view
    const { archive, dataset } = view
    // if we are collecting information for connecting a new archive
    if (archive !== null) {
        // use its selector
        return <Archive viewport={viewport} view={view} />
    }
    // if we are collecting information for connecting a new dataset
    if (dataset !== null) {
        // use its selector
        return <Dataset viewport={viewport} view={view} />
    }
    // otherwise, don't contribute anything
    return null
}


// end of file