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
// context
import { useReader } from './useReader'


// toggle the {coordinate} as the value for {axis}
export const useToggleCoordinate = (axis, coordinate) => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get my reader
    const reader = useReader()
    // selecting a reader mutates the server side store
    const [commit, pending] = useMutation(toggleCoordinateMutation)

    // make the handler
    const toggle = (viewport = activeViewport) => {
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
                selection: {
                    viewport,
                    reader: reader.name,
                    selector: axis,
                    value: coordinate,
                }
            },
            // update the store
            updater: store => {
                // get the root field of the mutation result
                const response = store.getRootField("viewToggleCoordinate")
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
                // send the error to the console
                console.error(`viz.reader.useToggleCoordinate:`)
                console.group()
                console.error(`ERROR while toggling '${reader.name}:${axis}:${coordinate}'`)
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
    return toggle
}


// the mutation that selects a reader
const toggleCoordinateMutation = graphql`
    mutation useToggleCoordinateMutation($selection: ViewSelectorInput!) {
        viewToggleCoordinate(selection: $selection) {
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
