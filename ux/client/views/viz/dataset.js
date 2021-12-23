// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
import { useFragment } from 'react-relay/hooks'
import { graphql } from 'relay-runtime'

// locals
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Dataset = (props) => {
    // pull the data
    const dataset = useFragment(graphql`
        fragment dataset_dataset on Dataset {
            id
            uuid
            selector {
                name
                value
            }
        }`,
        props.dataset)
    // unpack
    const { id, uuid } = dataset
    // parse the reader id
    const [family, name] = id.split(":")

    // render
    return (
        <div>{uuid}</div>
    )
}


// end of file