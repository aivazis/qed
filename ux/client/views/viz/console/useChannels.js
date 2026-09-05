// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'


// the journal channels the server knows about: fetched afresh when the tray mounts, and read
// from the store afterwards, where every live sync refetch of the app-wide state renews them,
// so a change made by any client, or a channel that speaks for the first time, reaches every
// client
export const useChannels = () => {
    // fetch, rendering what the store holds while the network answers
    const { qed } = useLazyLoadQuery(
        // the query
        channelsQuery,
        // no variables
        {},
        // the store first, then the server
        { fetchPolicy: "store-and-network" }
    )
    // hand back the channels
    return qed.journal
}


// the fragment; it is spread into the app-wide state query, so the listing rides along with
// every refetch
export const channelsGetJournalFragment = graphql`
    fragment channelsGetJournalFragment on QED {
        journal {
            id
            severity
            name
            active
            fatal
        }
    }
`


// the query the {window.qed} automation facade reads, straight from the server
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
