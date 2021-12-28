// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
import { useFragment } from 'react-relay/hooks'
import { graphql } from 'relay-runtime'

// project
// widgets
import { Info, Tray } from '~/widgets'
// locals
// hooks
import { useChannelInView } from './useChannelInView'
// components
import { Dataset } from './dataset'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Reader = (props) => {
    // access to the active view
    const getChannelInView = useChannelInView()
    // extract the id of the active reader, if any
    const { reader: { uuid: activeReader = null } = {} } = getChannelInView()

    // pull the data
    const reader = useFragment(graphql`
        fragment reader_reader on Reader {
            id
            uuid
            uri
            selectors {
                name
                values
            }
            datasets {
                uuid
                ...dataset_dataset
            }
        }`,
        props.reader)
    // unpack
    const { id, uuid, uri } = reader
    // parse the reader id
    const [family, name] = id.split(":")

    // check whether i'm the tray with the active {dataset,channel}
    const amActive = uuid === activeReader
    // mix the styles
    const trayStyle = amActive ? styles.reader.activeTray : styles.reader.tray

    // build the reader spec that gets installed in a view when a channel is chosen
    const readerSpec = { uuid, uri }

    // render
    return (
        <Tray title={name} initially={amActive} style={trayStyle} >
            <Info name="uri" value={uri} style={styles.attributes} />
            <Info name="reader" value={family} style={styles.attributes} />
            {reader.datasets.map((dataset) => (
                <Dataset key={dataset.uuid} reader={readerSpec} dataset={dataset} />
            ))}
        </Tray>
    )
}


// end of file