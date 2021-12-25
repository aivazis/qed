// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
import { useFragment } from 'react-relay/hooks'
import { graphql } from 'relay-runtime'

// project
// widgets
import { Info } from '~/widgets'
// locals
import { Channels } from './channels'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Dataset = (props) => {
    // get the reader
    const { reader } = props
    // pull the data
    const dataset = useFragment(graphql`
        fragment dataset_dataset on Dataset {
            uuid
            shape
            datatype
            channels
        }`,
        props.dataset)
    // unpack
    const { uuid, shape, datatype, channels } = dataset

    // render
    return (
        <>
            <Info name="shape" value={shape.join(" x ")} style={styles.attributes} />
            <Info name="type" value={datatype} style={styles.attributes} />
            <Channels reader={reader} dataset={uuid} channels={channels} />
        </>
    )
}


// end of file