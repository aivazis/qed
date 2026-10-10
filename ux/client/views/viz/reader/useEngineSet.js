// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// project
// hooks
import { useViewports } from '~/views/viz'


// pick the engine that draws the tiles of a viewport
export const useEngineSet = () => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // picking an engine mutates the server side store
    const [commit, pending] = useMutation(engineSetMutation)

    // make the handler
    const set = (engine, viewport = activeViewport) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        commit({
            // input
            variables: {
                // the payload
                input: {
                    viewport,
                    engine,
                }
            },
            onError: errors => {
                // send the error to the console
                console.error(`viz.reader.useEngineSet:`)
                console.group()
                console.error(`ERROR while picking the engine '${engine}' for viewport ${viewport}`)
                console.log(errors)
                console.groupEnd()
                // all done
                return
            }
        })
        // all done
        return
    }

    // all done
    return set
}


// the mutation that picks the engine; the new session makes every tile of the view fetched
// again, so the picture is redrawn by the engine just picked
export const engineSetMutation = graphql`
    mutation useEngineSetMutation($input: ViewEngineSetInput!) {
        viewEngineSet(input: $input) {
            views {
                id
                session
                engine
                flowable
            }
        }
    }
`


// end of file
