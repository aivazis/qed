// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// kill the server
export const Stop = () => {
    // ask the server to shut down
    fetch('/qed/stop').catch(
        // and swallow any errors
        () => null
    )

    // the container
    return (
        <section style={styles.stop}>
            <div style={styles.placeholder}>
                <a href="/" style={styles.link}>qed</a> has shut down; please close this window
            </div>
        </section>
    )
}


// end of file
