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
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Reader = (props) => {
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
        }`,
        props.reader)
    // unpack
    const { id, uri } = reader
    // parse the reader id
    const [family, name] = id.split(":")

    // render
    return (
        <Tray title={name} style={styles.reader.tray} >
            <Info name="uri" value={uri} style={styles.reader.attributes} />
            <Info name="reader" value={family} style={styles.reader.attributes} />
        </Tray>
    )
}


// end of file