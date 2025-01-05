// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'

// local
// components
import { Blank } from './blank'
import { Busy } from './busy'
import { Tab } from './tab'
import { Archive } from '../archive'
import { Reader } from '../reader'


// export the dataset viewer
export const Viewer = ({ view, viewport }) => {
    // unpack the view
    const { archive, reader } = view
    // render
    return (
        <>
            <Tab viewport={viewport} view={view} />
            {archive === null && reader === null && < Blank />}
            <React.Suspense fallback={<Busy />}>
                {archive !== null && <Archive view={view} viewport={viewport} />}
                {reader !== null && <Reader view={view} viewport={viewport} />}
            </React.Suspense>
        </>
    )
}


// end of file
