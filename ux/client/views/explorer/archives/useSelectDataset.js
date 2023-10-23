// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// local
// hooks
import { useArchive } from './useArchive'
import { useViews } from '../explorer/useViews'
import { useGetActiveView } from '../explorer/useGetActiveView'
import { useSetActiveView } from '../explorer/useSetActiveView'


// place {dataset} in the active view
export const useSelectDataset = (dataset) => {
    // get my archive
    const archive = useArchive()
    // get the empty view factory
    const { emptyView } = useViews()
    // unpack the active view
    const { archive: activeArchive, dataset: activeDataset } = useGetActiveView()
    // and the view activator
    const activate = useSetActiveView()

    // deduce my state
    const state = activeArchive?.id === archive.id && activeDataset?.uri === dataset.uri

    // build the selector
    const selector = () => {
        // adjust the view
        activate({ ...emptyView(), archive, dataset })
        // all done
        return
    }

    // all done
    return {
        // the selector
        selector: state ? () => null : selector,
        // and my current state
        state: state ? "selected" : "enabled",
    }
}


// end of file
