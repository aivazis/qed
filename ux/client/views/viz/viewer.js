// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// locals
// components
import { Blank } from './blank'
import { Tab } from './tab'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Viewer = ({ idx }) => {
    // render
    return (
        <>
            <Tab idx={idx} />
            <Blank />
        </>
    )
}


// end of file