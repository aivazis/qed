// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'

// project
// hooks
import { useServerVersion, useHeartbeat } from '~/context'
// locals
import styles from './styles'


// display the server state
export const Server = ({ style, ...rest }) => {
    // the query fragment i care about
    const { major, minor, micro, revision } = useServerVersion()

    // urls
    const repo = `https://github.com/aivazis/qed`
    const release = `${repo}/releases/tag/v${major}.${minor}.${micro}`

    // get the time
    const heartbeat = useHeartbeat()
    // use it to make a timestamp
    const title = `last checked on ${heartbeat.toString()}`

    // mix my paint
    const paint = styles.server(style, "good")
    // build the component and return it
    return (
        <div style={paint.box} title={title} {...rest}>
            <a href={repo} style={paint.link}>qed</a>
            server
            <a href={release} style={paint.link}>{major}.{minor}.{micro}</a>
            rev {revision}
        </div >
    )
}


// end of file
