// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'


// the journal channels the server knows about, read fresh every time the tray mounts
export const useChannels = () => {
    // fetch
    const { qed } = useLazyLoadQuery(
        // the query
        channelsQuery,
        // no variables
        {},
        // straight from the server, since channel state changes behind the store's back
        { fetchPolicy: "network-only" }
    )
    // hand back the channels
    return qed.journal
}


// the query; exported so the {window.qed} automation facade can read the same list
export const channelsQuery = graphql`
    query useChannelsQuery {
        qed {
            journal {
                id
                severity
                name
                active
                fatal
            }
        }
    }
`


// end of file
