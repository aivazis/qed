// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import { graphql, useLazyLoadQuery } from 'react-relay'

// local
// hooks
import { useViews } from '../../viz/useViews'


// get the visualization pipeline of the current {dataset} {channel}
export const useGetVizPipeline = () => {
    // get the views
    const { views, activeViewport } = useViews()
    // unpack the active view
    const { dataset, channel } = views[activeViewport]

    // set up the query variables
    const variables = {
        dataset: dataset.name,
        channel
    }

    // ask the server for the pipeline
    const { viz } = useLazyLoadQuery(vizPipelineQuery, variables)
    // and return it
    return viz
}


// the query
export const vizPipelineQuery = graphql`
    query useGetVizPipeline_controlsQuery($dataset: ID!, $channel: String!) {
        viz(dataset: $dataset, channel: $channel) {
            dataset
            channel
            controllers {
                __typename
                ... on Node {
                   id
                   uuid
                }
                ... on ValueController {
                    slot
                    min
                    max
                    value
                }
                ... on RangeController {
                    ...range_range
                }
            }
        }
    }
`


// end of file
