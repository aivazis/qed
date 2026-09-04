// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// send hand-set display bounds of a value controller to the server side store
export const useResizeValueController = ({ viewport, channel }) => {
    // resizing the controller mutates the server side store
    const [commit] = useMutation(useResizeValueControllerMutation)

    // a hand edit is a single deliberate commit, not a drag storm, so there is nothing to coalesce;
    // the server refuses an extent that encroaches on the picks, and the refusal lands in {onError}
    const resize = ({ controller, extent, onError = null }) => {
        // commit the mutation
        commit({
            // the payload
            variables: {
                input: { viewport, channel, controller, ...extent },
            },
            // on failure, report and let the caller cope
            onError: errors => {
                // show me
                console.log(`viz.controls.viz.useResizeValueController:`)
                console.group()
                console.log(`viewport ${viewport}:`)
                console.log(`ERROR while resizing ${controller}`)
                console.log(`for channel ${channel}`)
                console.log(errors)
                console.groupEnd()
                // let the caller know
                if (onError) {
                    onError(errors)
                }
            },
        })
        // all done
        return
    }

    // all done
    return { resize }
}


// the mutation that sets the controller display bounds
export const useResizeValueControllerMutation = graphql`
mutation useResizeValueControllerMutation($input: ViewValueResizeInput!) {
    viewValueResize(input: $input) {
        view {
            session
        }
        controller {
            id
            dirty
            auto
            min
            max
        }
    }
}`


// end of file
