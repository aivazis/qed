// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import { useFragment } from 'react-relay/hooks'
import { graphql } from 'relay-runtime'

// project
// widgets
import { Info } from '~/widgets'

// locals
import { Channels } from './channels'
import { Selectors } from './selectors'
// styles
import styles from './styles'


// display the datasets associated with this reader
export const Dataset = (props) => {
    // extract the reader spec
    const { reader } = props
    // pull the data
    const dataset = useFragment(graphql`
        fragment dataset_dataset on Dataset {
            uuid
            datatype
            selector {
                name
                value
            }
            shape
            tile
            channels
        }`,
        props.dataset)
    // unpack
    const { uuid, datatype, selector, shape, tile, channels } = dataset

    // build the dataset spec that get installed in the {views}
    const datasetSpec = { uuid, datatype, selector, shape, tile }

    // render
    return (
        <>
            <Selectors selector={selector} />
            <Info name="shape" value={shape.join(" x ")} style={styles.attributes} />
            <Info name="type" value={datatype} style={styles.attributes} />
            <Channels reader={reader} dataset={datasetSpec} channels={channels} />
        </>
    )
}


// end of file