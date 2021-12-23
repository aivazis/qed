// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

//project
// widgets
import { Info, Tray } from '~/widgets'
// locals
// styles
import styles from './styles'

// display the datasets associated with this reader
export const Reader = ({ reader }) => {
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
