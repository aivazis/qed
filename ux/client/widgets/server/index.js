// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// hooks
import { useServerVersion } from '~/context'
// locals
import styles from './styles'


// display the server state
export const Server = ({ style, ...rest }) => {
    // the query fragment i care about
    const { major, minor, micro, revision } = useServerVersion()

    // get the time
    const now = new Date()
    // use it to make a timestamp
    const title = `last checked on ${now.toString()}`

    // mix my paint
    const paint = styles.server(style, "good")
    // build the component and return it
    return (
        <div style={paint} title={title} {...rest}>
            qed server {major}.{minor}.{micro} rev {revision}
        </div>
    )
}


// end of file
