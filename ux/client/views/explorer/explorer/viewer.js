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
import { NewArchiveForm } from '../archive'


// export the dataset viewer
export const Viewer = ({ view, viewport }) => {
    // unpack the view
    const { archive, dataset } = view
    // render
    return (
        <>
            <Tab viewport={viewport} view={view} />
            {archive === null && dataset === null && < Blank />}
            <React.Suspense fallback={<Busy />}>
                {archive !== null && <NewArchiveForm view={view} viewport={viewport} />}
                {dataset !== null && <Blank />}
            </React.Suspense>
        </>
    )
}


// end of file
