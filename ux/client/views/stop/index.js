// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
import { Link } from 'react-router-dom'
// locals
import styles from './styles'


// kill the server
export const Stop = () => {
    // ask the server to shut down
    fetch('stop').catch(
        // and swallow any errors
        () => null
    )

    // the container
    return (
        <section style={styles.stop}>
            <div style={styles.placeholder}>
                <Link to="/" style={styles.link}>qed</Link>
                &nbsp;has shut down; please close this window
            </div>
        </section>
    )
}


// end of file
