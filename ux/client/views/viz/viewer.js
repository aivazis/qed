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
import { Viewport } from './viewport'
// hooks
import { useRegisterViewport } from './useRegisterViewport'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Viewer = ({ idx, view }) => {
    // register my viewport
    // N.B: the ref has to be obtained here and handed to the {viewport} because
    // {tab} needs it to power up the {sync} button
    const viewport = useRegisterViewport()

    // get my view info
    const { reader, dataset, channel } = view
    // and unpack what i need
    const { uuid: readerUUID, uri } = reader
    const { uuid: datasetUUID, datatype, selector, shape, tile } = dataset

    // put together the dataset URI
    // N.B.: it is important to do it here so the {viewport} props change when a new dataset
    //       channel is selected; the {view} index by itself is not enough to trigger a refresh
    // first, assemble the resolved selector+channel tag
    const tag = [...selector.map(b => b.value), channel].join(":")
    // put together the dataset uri
    const datasetURI = ["data", readerUUID, datasetUUID, tag].join("/")

    // render
    return (
        <>
            {/* the title bar with the dataset description and the controls */}
            <Tab idx={idx} view={view} viewport={viewport} />
            {/* identifying metadata */}
            <Info name="uri" value={uri} style={styles.attributes} />
            <Info name="type" value={datatype} style={styles.attributes} />
            <Info name="shape" value={shape.join(" x ")} style={styles.attributes} />
            <Info name="tile" value={tile.join(" x ")} style={styles.attributes} />

            {/* the data viewport */}
            <Viewport ref={viewport} view={view} uri={datasetURI} />
        </>
    )
}


// end of file