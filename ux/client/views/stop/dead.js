// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
// locals
import styles from './styles'


// show the dead screen
export const Dead = ({ base }) => {
    // render
    return (
        <section style={styles.stop}>
            <div style={styles.placeholder}>
                <a href={base} style={styles.link}>qed</a>
                {" "}
                has shut down; please close this window
            </div>
        </section>
    )
}


// end of file
