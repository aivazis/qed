// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// external
import React from 'react'
import { graphql, useFragment, useMutation } from 'react-relay/hooks'


// ask the server to stage the connected data sources
// mounting the viz activity is the client's declaration that the catalog is relevant, so
// observing readers that have not yet made first contact sends the {stage} mutation; the
// server responds with the updated catalog, and the statuses merge into the store by id
export const useStageReaders = (qed) => {
    // extract the reader lifecycle information
    const { readers } = useFragment(vizStageReadersFragment, qed)
    // build the mutation request
    const [request, isInFlight] = useMutation(stageMutation)
    // collect the names of the readers that are still awaiting first contact
    const pending = readers.filter(reader => reader.status === "connected").map(reader => reader.name)
    // form the signature of the pile, so the effect fires only when its composition changes
    const signature = pending.join(",")
    // the signature of the last request, so a source the server cannot flip out of
    // {connected} is asked about only once per distinct pile rather than in a loop
    const attempted = React.useRef(null)
    // schedule the staging request
    React.useEffect(() => {
        // when the pile drains, forget the last attempt, so a catalog that regresses to
        // {connected}, e.g. after a server restart, asks again. this belongs here rather
        // than in the body: a render may be discarded or repeated, and a mark moved
        // during one would be moved twice or not at all
        if (pending.length === 0) {
            // clear the mark
            attempted.current = null
            // and there is nothing to ask for
            return
        }
        // if a request is already on its way, or this pile has already been asked about
        if (isInFlight || attempted.current === signature) {
            // there is nothing to do
            return
        }
        // leave the mark
        attempted.current = signature
        // and ask the server to stage the catalog
        request({
            // the payload: no target, so the whole catalog stages
            variables: { input: {} },
        })
        // all done
        return
    }, [signature, isInFlight])
    // all done
    return
}


// the lifecycle information the trigger observes
const vizStageReadersFragment = graphql`
    fragment vizStageReadersFragment on QED {
        readers {
            id
            name
            status
        }
    }
`

// the request that initiates first contact; the response carries the updated statuses,
// which relay merges into the resident catalog by reader id
const stageMutation = graphql`
    mutation useStageReadersMutation($input: StageInput!) {
        stage(input: $input) {
            readers {
                id
                name
                status
            }
        }
    }
`


// end of file
