// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// locals
// components
import { Blank } from './blank'
// styles
import styles from './styles'


// export the data viewer
export const Viewer = ({ idx, view, registrar }) => {
    // if my view is trivial
    if (!view) {
        return <Blank />
    }

    // unpack it
    const { reader, dataset, channel } = view
    // and check again for the trivial cases
    if (!reader || !dataset || !channel) {
        return <Blank />
    }

    // nothing yet
    return null
}


// end of file
