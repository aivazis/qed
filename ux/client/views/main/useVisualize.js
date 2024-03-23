// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// local
// hooks
import { useViewports } from './useViewports'


// hook that adjusts the contents of a given viewport
// currently, only called by {reader} instances when selected/updated
export const useVisualize = () => {
    // grab the active viewport index and the {views} mutator
    const { activeViewport } = useViewports()
    // placing a view in a viewport mutates the server side application store
    const [request, pending] = useMutation(visualizeMutation)

    // make the handler
    const visualize = (view, viewport = activeViewport) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, place the, possible partial, view information in the server side store
        request({
            // input
            variables: {
                // the payload
                viewport: viewport,
                reader: view?.reader?.uri || null,
                dataset: view?.dataset?.name || null,
                channel: view?.channel?.tag || null,
            },
            // update the store
            updater: store => {
                // get the root field of the mutation result
                const response = store.getRootField("viewUpdate")
                // ask for the list of views
                const updated = response.getLinkedRecords("views")
                //if it's trivial
                if (updated == null) {
                    // something went wrong at the server; bail, for now
                    return
                }
                // if all is good, get the remote store
                const qed = store.get("QED")
                // attach the updated pile
                qed.setLinkedRecords(updated, "views")
                // all done
                return
            },
            // if something goes wrong
            onError: error => {
                // show me
                console.log(`main.useVisualize: ERROR:`, error)
            }

        })
        // all done
        return
    }

    // and return it
    return visualize
}


// the mutation that places a view in a viewport
const visualizeMutation = graphql`
    mutation useVisualizeMutation(
        $viewport: Int!, $reader: String, $dataset: String, $channel: String
    ) {
        viewUpdate(reader: $reader, dataset: $dataset, channel: $channel, viewport: $viewport) {
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
        }
    }
`

// end of file
