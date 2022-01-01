// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// the area
const stop = (props) => {
    // ask the server to shut down
    fetch('/stop').catch(
        // swallow any errors
        (error) => null
    )

    // the container
    return (
        <section style={styles.stop}>
            <div style={styles.placeholder}>
                <a href="/">qed</a> has shut down; please close this window
            </div>
        </section>
    )
}


// publish
export default stop


// end of file
