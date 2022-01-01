// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'

// project
// widgets
import { Header, Tray } from '~/widgets'

// locals
// styles
import styles from './styles'

// the dataset explorer
export const Controls = () => {
    // render
    return (
        <>
            {/* the title of the panel */}
            <Header title="controls" style={styles.controls.header} />
        </>
    )
}


// end of file
