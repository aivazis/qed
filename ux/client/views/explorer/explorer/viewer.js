// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// components
import { Blank } from './blank'
import { Busy } from './busy'
import { Tab } from './tab'


// export the table viewer
export const Viewer = ({ view, viewport }) => {
    // unpack the view
    const { archive, dataset } = view
    // render
    return (
        <>
            <Tab viewport={viewport} view={view} />
            {!archive && <Blank />}
            <React.Suspense fallback={<Busy />}>
            </React.Suspense>
        </>
    )
}


// end of file
