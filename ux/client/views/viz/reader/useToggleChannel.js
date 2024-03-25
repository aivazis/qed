// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'

// project
// hooks
import { useViewports } from '../../main'

// local
// context
import { useReader } from './useReader'


// toggle the {tag} as the value for {channel}
export const useToggleChannel = (channel) => {
    // get the active viewport
    const { activeViewport } = useViewports()
    // get my reader
    const reader = useReader()
    // selecting a reader mutates the server side store
    const [commit, pending] = useMutation(toggleChannelMutation)

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
                    selector: "channels",
                    value: channel.tag,
                }
            },
            // update the store
            updater: store => {
                // get the root field of the mutation result
                const response = store.getRootField("viewToggleChannel")
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
                console.error(
                    `viz.reader.useToggleCoordinate: ERROR while toggling '${axis}:${coordinate}'`
                )
                console.group()
                console.log(errors)
                console.groupEnd()
            }
        })
        // all done
        return
    }

    // all done
    return toggle
}


// the mutation that selects a reader
const toggleChannelMutation = graphql`
    mutation useToggleChannelMutation($selection: ViewSelectorInput!) {
        viewToggleChannel(selection: $selection) {
            view {
                id
                # and get whatever readers need
                ...contextGetViewFragment
            }
        }
    }
`


// end of file
