// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Header } from '~/widgets'

// locals
// hooks
import { useReaders } from './useReaders'
// components
import { Reader } from './reader'
// styles
import styles from './styles'

// the dataset explorer
export const Datasets = () => {
    // get the readers
    const readers = useReaders()
    // render
    return (
        <>
            {/* the title of the panel */}
            <Header title="datasets" style={styles.datasets.header} />
            {/* go through the readers and render each one */}
            {readers.edges.map(edge => (
                <Reader key={edge.node.uuid} reader={edge.node} />
            ))}
        </>
    )
}


// end of file
