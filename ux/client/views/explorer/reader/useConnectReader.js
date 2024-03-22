// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// external
import React from 'react'
import { graphql, useMutation } from 'react-relay/hooks'


// build the handlers necessary to connect a new reader
export const useConnectReader = (setForm, hide) => {
    // error placeholder
    const [error, setError] = React.useState(null)
    // build the mutation request
    const [request, isInFlight] = useMutation(connectMutation)
    // set up the state update
    const update = (field, value) => {
        // clear any errors
        setError(null)
        // replace my state
        setForm(old => {
            // with
            const clone = {
                // a copy of the old state
                ...old,
                // with the value of the given field replaced with the new one
                [field]: value,
            }
            // if we are setting the type
            if (field === "product" && clone.bytes && clone.sizeof) {
                // we now know the number of cells
                const cells = clone.bytes / clone.sizeof[value]
                // update the form
                clone.cells = cells.toString()
            }
            // if we are setting the lines and we know the number of cells in the product
            if (field === "lines" && clone.cells > 0) {
                // compute the guess
                const samples = clone.cells / value
                // adjust the samples
                clone.samples = Number.isFinite(samples) ? samples.toString() : ""
            }
            // if we are setting the samples and we know the number of cells in the product
            if (field === "samples" && clone.cells > 0) {
                // compute the guess
                const lines = clone.cells / value
                // adjust the lines
                clone.lines = Number.isFinite(lines) ? lines.toString() : ""
            }
            // hand it off
            return clone
        })
        // all done
        return
    }
    // set up the reader connector
    const makeConnector = spec => () => {
        // if there is already a pending operation
        if (isInFlight) {
            // skip this update
            return
        }
        // otherwise, send the mutation to the server
        request({
            // input
            variables: {
                // the payload
                spec
            },
            updater: store => {
                // get the root field of the query result
                const payload = store.getRootField("connectReader")
                // if it's trivial
                if (!payload) {
                    // raise an issue
                    throw new Error("could not find any datasets")
                }
                // ask for the new reader
                const reader = payload.getLinkedRecord("reader")
                // get the session manager
                const qed = store.get("QED")
                // get its connected archives
                const readers = qed.getLinkedRecords("readers")
                // add the new one to the pile
                qed.setLinkedRecords([...readers, reader], "readers")
                // all done
                return
            },
            // when done
            onCompleted: data => {
                // clear any errors
                setError(null)
                // remove the form from view
                hide()
                // all done
                return
            },
            // if something went wrong
            onError: error => {
                // record the error
                setError([
                    `got: ${error}`,
                    `while opening the data product '${spec.name}'`,
                    `at '${spec.uri}'`,
                    `using the '${spec.reader}' reader`
                ])
                // all done
                return
            }
        })
    }
    // build the handler that removes the form from view
    const cancel = evt => {
        // stop this event from bubbling up
        evt.stopPropagation()
        // and quash any side effect
        evt.preventDefault()
        // remove the view in my viewport from the pile
        hide()
        // all done
        return
    }

    // return the handlers
    return { error, update, makeConnector, cancel }
}


// the mutation that associates a reader with a data product
const connectMutation = graphql`
    mutation useConnectReaderMutation($spec: ReaderInput!) {
        connectReader(spec: $spec) {
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
                    name
                    datatype
                    selector {
                        name
                        value
                    }
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
                    shape
                    origin
                    tile
                }
            }
        }
    }
`


// end of file
