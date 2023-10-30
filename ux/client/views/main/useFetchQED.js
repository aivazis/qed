// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved

// externals
// relay
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'


// get the session manager
export const useFetchQED = () => {
    // ask for the session manager
    const { qed } = useLazyLoadQuery(
        // the query
        query,
        // the vars
        {},
        // the options
        { fetchPolicy: "network-only" }
    )
    // and return it
    return qed
}


// query all known data archives
const query = graphql`
query useFetchQEDQuery {
    qed {
        # metadata
        id
        # info for the archive panel
        ...context_archives
        # and data readers
        readers {
            # metadata
            id
            name
        }
    }
}`


// end of file
