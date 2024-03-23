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


// query all known data archives
const query = graphql`
query useFetchQEDQuery {
    qed {
        # metadata
        id
        views {
            id
            name
            reader {
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
                    datatype
                    selector {
                        name
                        value
                    }
                    shape
                    origin
                    tile
                    channels {
                        id
                        name
                        tag
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
                }
            }
            dataset {
                id
                name
                datatype
                selector {
                    name
                    value
                }
                channels {
                    id
                    name
                    tag
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
            }
            channel {
                id
                name
                tag
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
        }

        # the active views for dataset selection by {viz/reader}
        ...context_viz_reader_views
        # the connected data archives
        ...context_archives
        # and data readers
        ...context_viz_connected_readers
    }
}`


// end of file
