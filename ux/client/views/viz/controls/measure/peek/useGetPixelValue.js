// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useLazyLoadQuery } from 'react-relay'

// local
// context
import { Context } from './context'


// the code below looks tricky because it is trying to avoid the flicker caused by suspense

// set it up so we can get the value of a pixel
export const useGetPixelValue = () => {
    // pull info out of my context
    const { variables, options } = React.useContext(Context)
    // get the data and return it
    return useLazyLoadQuery(pixelValueQuery, variables, options)
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
