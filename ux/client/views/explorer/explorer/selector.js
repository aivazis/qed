// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// locals
// components
import { Selector as Archive } from '../archive'
import { Selector as Reader } from '../reader'


// the decorator of an {explorer} tab
export const Selector = ({ viewport, view }) => {
    // unpack the view
    const { archive, reader } = view
    // if we are collecting information for connecting a new archive
    if (archive !== null) {
        // use its selector
        return <Archive viewport={viewport} view={view} />
    }
    // if we are collecting information for connecting a new reader
    if (reader !== null) {
        // use its selector
        return <Reader viewport={viewport} view={view} />
    }
    // otherwise, don't contribute anything
    return null
}


// end of file