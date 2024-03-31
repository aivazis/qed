// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved

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


const query = graphql`
    query useFetchQEDQuery {
        qed {
            # the server side store id
            id
            # the connected data archives
            ...context_archives
            # reader information for populating the panel of datasets
            ...readersGetReadersFragment
            # reader information for disconnecting readers from the panel
            ...disconnectReaderViewsFragment
            # information for rendering the viewport
            ...vizGetViewsFragment
        }
    }
`


// end of file
