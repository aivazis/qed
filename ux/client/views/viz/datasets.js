// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// externals
import React from 'react'
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'

//project
// widgets
import { Flex, Header, Tray } from '~/widgets'
// locals
// styles
import styles from './styles'

// the dataset explorer
export const Datasets = () => {
    // ask the server for the collection of known data sets
    const { datasets } = useLazyLoadQuery(datasetsQuery)

    // render
    return (
        <>
            {/* the title of the panel */}
            <Header title="datasets" />
        </>
    )
}


// the dataset query
const datasetsQuery = graphql`query datasetsQuery {
    datasets {
        # the dataset id
        id
    }
}`


// end of file
