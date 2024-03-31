// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// project
// hooks
import { useViewports } from '~/views/viz'

// local
// hooks
import { useReader } from './useReader'


// select the reader that's active in a viewport
export const useSelectReader = () => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get my reader
    const reader = useReader()
    // selecting a reader mutates the server side store
    const [commit, pending] = useMutation(selectReaderMutation)

    // make the handler
    const select = (viewport = activeViewport) => {
        // if there is already a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server
        commit({
            //input
            variables: {
                // the payload
                viewport,
                reader: reader.name
            },
            // update the store
            updater: store => {
                // get the root field of the mutation result
                const response = store.getRootField("viewSelectReader")
                // ask for the view
                const view = response.getLinkedRecord("view")
                // if it's trivial
                if (view === null) {
                    // something went wrong at the server; not much more to do
                    return
                }
                // get the remote store
                const qed = store.get("QED")
                // get the current set of views
                const views = qed.getLinkedRecords("views")
                // replace the view at {viewport} with the new one
                qed.setLinkedRecords(views.toSpliced(viewport, 1, view), "views")
                // all done
                return
            },
            onError: errors => {
                // show me
                console.log(`viz.reader.useSelectReader:`)
                console.group()
                console.log(`ERROR while selecting '${reader.name}':`)
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
    return select
}

// the mutation that selects a reader
const selectReaderMutation = graphql`
    mutation useSelectReaderMutation($viewport: Int!, $reader: String!) {
        viewSelectReader(viewport: $viewport, reader: $reader) {
            view {
                id
                # and get whatever readers need
                ...contextReaderGetViewFragment
                # for the measure layer control
                ...measureViewerGetMeasureLayerStateFragment
            }
        }
    }
`


// end of file