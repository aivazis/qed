// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import { useLazyLoadQuery, usePreloadedQuery, useQueryLoader } from "react-relay/hooks"


// fetch the contents of a table lazily
export const useFetchServerVersion = (path) => {
    // get the query result
    const data = useLazyLoadQuery(
        // the query
        query,
        // the vars
        {},
        // the options
        { fetchPolicy: "network-only" }
    )
    // and make it available
    return data
}

// query preloader
export const useServerQueryLoader = () => {
    // load the query
    const context = useQueryLoader(query)
    // and return the loading context
    return context
}

// use the preloaded query
export const useServerQuery = (qref) => {
    // get the data
    const data = usePreloadedQuery(query, qref)
    // and return it
    return data
}

// the query
const query = graphql`query useSyncWithServerQuery {
    version {
        major
        minor
        micro
        revision
    }
}`


// end of file
