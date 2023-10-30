// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// externals
// relay
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'


// get the session manager
export const useFetchQED = () => {
    // g
    const { qed } = useLazyLoadQuery(
        // the query
        query,
        // the vars
        {},
        // the options
        { fetchPolicy: "network-only" }
    )
    // and return them
    return qed
}


// query all known data archives
const query = graphql`
query useFetchQEDQuery {
    qed {
        # metadata
        id
        # the connected archives
        archives {
            # metadata
            id
            name
            # plus whatever else archives need to render themselves
        }
        # and data readers
        readers {
            # metadata
            id
            name
            # plus whatever else readers need to render themselves
            ...context_reader
        }
    }
}`


// end of file
