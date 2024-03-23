// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Header } from '~/widgets'

// locals
// hooks
import { useReaders } from '../viz/useReaders'
// components
import { Reader } from '../reader'
// styles
import styles from './styles'


// export the activity panel
export const Datasets = () => {
    // get the readers
    const readers = useReaders()
    // render
    return (
        <>
            {/* the title of the panel */}
            <Header title="datasets" style={styles.header} />
            {/* go through the readers and render them */}
            {readers.map(reader => (
                <Reader key={reader.id} reader={reader} />
            ))}
        </>
    )
}


// end of file
