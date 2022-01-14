// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// local
// context
import { VizContext } from './vizContext'


// storage for the refs to the {mosaic} placemats that frame the visible part of the data
export const useViewports = () => {
    // grab the list of {views} and the array of refs from my context
    const { views, viewports } = React.useContext(VizContext)

    // initialize the array
    viewports.current = new Array(views.lenth).fill(null)
    // build the ref registrar
    const registrar = idx => ref => viewports[idx] = ref

    // and return them
    return { viewports, registrar }
}


// end of file
