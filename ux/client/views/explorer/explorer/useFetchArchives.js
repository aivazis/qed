// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// externals
// relay
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'


// ask the server for all known archives
export const useFetchArchives = () => {
    // load the data sources
    const { archives } = useLazyLoadQuery(
        // the query
        query,
        // the vars
        {},
        // the options
        { fetchPolicy: "network-only" }
    )
    // and return them
    return archives
}


// query all known data archives
const query = graphql`query useFetchArchivesQuery {
archives(first:100) @connection(key: "query_archives") {
    count
    edges {
        node {
            # the archive id
            id
            # the name of the data archive
            name
            # whatever archives need to render themselves
            ...context_archive
        }
        cursor
    }
    pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
    }
}
}`


// end of file
