// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// components
import { Blank } from './blank'
import { Tab } from './tab'
// hooks
import { useSetActiveView } from './useSetActiveView'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Viewer = ({ idx }) => {
    // make a handler that makes me the active view
    const behaviors = {
        onClick: useSetActiveView(idx)
    }

    // render
    return (
        <>
            <Tab idx={idx} behaviors={behaviors} />
            <Blank behaviors={behaviors} />
        </>
    )
}


// end of file