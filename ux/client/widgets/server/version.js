// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// locals
// hooks
import { useServerQuery } from './useSyncWithServer'
// styles
import styles from './styles'


export const Version = ({ qref, style }) => {
    // query the server
    const { version } = useServerQuery(qref)
    // unpack the version info
    const { major, minor, micro, revision } = version

    // merge the overall styles
    const base = { ...style.box, ...styles.box, ...style.text, ...styles.text }
    // and the state colorization
    const good = { ...style.status.good, ...styles.status.good }

    // get the time
    const now = new Date()
    // use it to make a timestamp
    const title = `last checked on ${now.toString()}`
    // assemble the version
    return (
        <div style={{ ...base, ...good }} title={title}>
            qed server {major}.{minor}.{micro} rev {revision}
        </div>
    )
}


// end of file
