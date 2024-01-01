// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useLazyLoadQuery } from 'react-relay'

// local
// context
import { Context } from './context'


// the code below looks tricky because it is trying to avoid suspending component rendering
// while the query is in flight and rendering again once the result is available because this
// causes flicker

// set it up so we can get the value of a pixel
export const useGetPixelValue = () => {
    // pull info out of my context
    const { variables, options } = React.useContext(Context)

    // get the data; the first time, {options} is null so we ask the server
    // on {refresh}, we adjust the {options} so queries get resolved from the store,
    // which bypasses suspense
    const { sample } = useLazyLoadQuery(pixelValueQuery, variables, options)

    // and return it
    return sample
}


// the query
export const pixelValueQuery = graphql`
    query useGetPixelValue_sampleDatasetQuery($dataset: ID!, $line: Int!, $sample: Int!) {
        sample(dataset: $dataset, line: $line, sample: $sample){
            pixel
            value {
                channel
                reps {
                    rep
                    units
                }
            }
        }
    }
`


// end of file
