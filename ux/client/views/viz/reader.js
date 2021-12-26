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
// context
import { Context } from './context'
// components
import { Dataset } from './dataset'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Reader = (props) => {
    // access to the active view
    const { activeView, views } = React.useContext(Context)
    // unpack the active view spec
    const { reader: activeReader } = { ...views[activeView] }
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

    // mix the styles
    const trayStyle = (uuid === activeReader) ? styles.reader.activeTray : styles.reader.tray

    // render
    return (
        <Tray title={name} style={trayStyle} >
            <Info name="uri" value={uri} style={styles.attributes} />
            <Info name="reader" value={family} style={styles.attributes} />
            {reader.datasets.map((dataset) => (
                <Dataset key={dataset.uuid} reader={uuid} dataset={dataset} />
            ))}
        </Tray>
    )
}


// end of file