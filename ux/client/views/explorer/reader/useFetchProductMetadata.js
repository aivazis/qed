// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
// relay
import { graphql, useLazyLoadQuery, usePreloadedQuery, useQueryLoader } from 'react-relay/hooks'


// fetch the contents of a directory lazily
export const useFetchProductMetadata = (path) => {
    // get the contents
    const data = useLazyLoadQuery(
        // the query
        query,
        // the vars
        { path, },
        // the options
        { fetchPolicy: "network-only" }
    )
    // and return them
    return data
}

// query preloader
export const useProductMetadataLoader = () => {
    // load the query
    const context = useQueryLoader(query)
    // and return the loading context
    return context
}

// use the preloaded query
export const useQueryProductMetadata = (qref) => {
    // show me
    console.log("product metadata: qref: ", qref)
    // get the payload
    const payload = usePreloadedQuery(query, qref)
    // and again
    console.log("product metadata: payload: ", payload)
    // unpack the query result
    const { discover } = payload
    // and return it
    return discover
}

// query the contents of the directory at {uri}
const query = graphql`query useFetchProductMetadataQuery(
    $archive: String!, $uri: String!, $module: String!
) {
    discover(archive: $archive, uri: $uri, module: $module) {
        id
        uri
        product
        bytes
        cells
        shape
    }
}`


// end of file