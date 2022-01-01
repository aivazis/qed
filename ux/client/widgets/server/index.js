// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'

// locals
import styles from './styles'


// display the server state
const server = ({ style, ...props }) => {
    // the query fragment i care about
    const { major, minor, micro, revision } = useLazyLoadQuery(query).version

    // merge the overall styles
    const base = { ...style.box, ...styles.box, ...style.text, ...styles.text }
    // and the state colorization
    const good = { ...style.status.good, ...styles.status.good }

    // get the time
    const now = new Date()
    // use it to make a timestamp
    const title = `last checked on ${now.toString()}`

    // mark
    console.log(`server: ${title}`)

    // build the component and return it
    return (
        <div style={{ ...base, ...good }} title={title}>
            qed server {major}.{minor}.{micro} rev {revision}
        </div>
    )
}


// the query
const query = graphql`query serverQuery {
    version {
        major
        minor
        micro
        revision
    }
}`


// publish
export default server


// end of file
