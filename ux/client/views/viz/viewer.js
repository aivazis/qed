// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Info } from '~/widgets'

// locals
// components
import { Tab } from './tab'
// hooks
import { useViews } from './useViews'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Viewer = ({ idx }) => {
    // get the views
    const { views } = useViews()
    // get my view info
    const { reader, dataset } = views[idx]
    // unpack
    const { uri } = reader
    const { datatype, shape, tile } = dataset

    // render
    return (
        <>
            <Tab idx={idx} />
            <Info name="uri" value={uri} style={styles.attributes} />
            <Info name="type" value={datatype} style={styles.attributes} />
            <Info name="shape" value={shape.join(" x ")} style={styles.attributes} />
            <Info name="tile" value={tile.join(" x ")} style={styles.attributes} />
        </>
    )
}


// end of file