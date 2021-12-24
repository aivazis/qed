// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
import { useFragment } from 'react-relay/hooks'
import { graphql } from 'relay-runtime'

// locals
// widgets
import { Info } from '~/widgets'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Dataset = (props) => {
    // pull the data
    const dataset = useFragment(graphql`
        fragment dataset_dataset on Dataset {
            shape
            datatype
        }`,
        props.dataset)
    // unpack
    const { shape, datatype } = dataset

    // render
    return (
        <>
            <Info name="shape" value={shape.join("x")} style={styles.attributes} />
            <Info name="type" value={datatype} style={styles.attributes} />
        </>
    )
}


// end of file