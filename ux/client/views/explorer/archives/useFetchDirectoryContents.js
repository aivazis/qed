// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
// relay
import { graphql, useLazyLoadQuery, usePreloadedQuery, useQueryLoader } from 'react-relay/hooks'


// fetch the contents of a directory lazily
export const useFetchDirectoryContents = (path) => {
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
export const useDirectoryContentsLoader = () => {
    // load the query
    const context = useQueryLoader(query)
    // and return the loading context
    return context
}

// use the preloaded query
export const useQueryDirectoryContents = (qref) => {
    // get the data
    const data = usePreloadedQuery(query, qref)
    // and return it
    return data
}

// query the contents of the directory at {uri}
const query = graphql`query useFetchDirectoryContentsQuery($archive: String!, $path: String!) {
    contents(archive: $archive, path:$path) {
        id
        name
        uri
        isFolder
    }
}`


// end of file