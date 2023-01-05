// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import { graphql, useLazyLoadQuery } from 'react-relay'

// local
// hooks
import { useGetView } from '../../viz/useGetView'


// get the visualization pipeline of the current {dataset} {channel}
export const useGetVizPipeline = () => {
    // unpack the active view
    const { dataset, channel } = useGetView()
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
                }
                ... on RangeController {
                    slot
                    ...range_range
                }
                ... on ValueController {
                    slot
                    ...value_value
                }
            }
        }
    }
`


// end of file
