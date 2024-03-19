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
    console.log(qed)
    // and return it
    return qed
}


// query all known data archives
const query = graphql`
query useFetchQEDQuery {
    qed {
        # metadata
        id
        archives {
            id
            name
            uri
            readers
        }
        readers {
            id
            name
            uri
            api
            selectors {
                name
                values
            }
            datasets {
                id
                name
                channels {
                    id
                    name
                    controllers {
                        __typename
                        ... on Node {
                            id
                        }
                        ... on RangeController {
                            slot
                            min
                            max
                            low
                            high
                        }
                        ... on ValueController {
                            id
                            slot
                            min
                            max
                            value
                        }
                    }
                    view {
                        id
                        name
                        measure {
                            id
                            name
                            active
                            path {
                                x
                                y
                            }
                            closed
                            selection
                        }
                        sync {
                            id
                            name
                            channel
                            zoom
                            scroll
                            path
                            offsets {
                                x
                                y
                            }
                        }
                        zoom {
                            id
                            name
                            horizontal
                            vertical
                            coupled
                        }
                    }
                }
                datatype
                selector {
                    name
                    value
                }
                shape
                origin
                tile
            }
        }


        # the connected data archives
        ...context_archives
        # and data readers
        ...context_readers
    }
}`


// end of file
