// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

//project
// widgets
import { Flex, Tray } from '~/widgets'
// locals
// styles
import styles from './styles'

// the dataset explorer
export const Datasets = () => {
    // mix the style
    const panelStyle = {
        panel: {
            // pull the generic opinions
            ...styles.flex.panel,
            // and my specializations
            ...styles.datasets.panel,
        },
    }

    // render
    return (
        < Flex.Panel min={200} max={400} style={panelStyle} >
        </Flex.Panel >
    )
}


// end of file
