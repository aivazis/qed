// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'

//project
// widgets
import { Header } from '~/widgets'
// locals
// readers
import { Reader } from './reader'
// styles
import styles from './styles'

// the dataset explorer
export const Datasets = () => {
    // ask the server for the collection of known data sets
    const { readers } = useLazyLoadQuery(datasetsQuery)

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


// the dataset query
const datasetsQuery = graphql`query datasetsQuery {
    readers(first: 100) @connection(key: "datasets_readers") {
        count
        edges {
            node {
                # i need the {uuid} to make the child key
                uuid
                # plus whatever the {reader} needs to render itself
                ...reader_reader
            }
            cursor
        }
    }
}`


// end of file
