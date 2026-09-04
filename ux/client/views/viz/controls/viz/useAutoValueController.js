// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// pin a value controller, or release it to follow the data statistics
export const useAutoValueController = ({ viewport, channel }) => {
    // flipping the flag mutates the server side store
    const [commit, pending] = useMutation(useAutoValueControllerMutation)

    // make the handler
    const setAuto = ({ controller, auto }) => {
        // if there is a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server; the payload carries the adjusted bounds,
        // which the relay store folds into the controller fragment
        commit({
            // the payload
            variables: {
                input: { viewport, channel, controller, auto },
            },
            // on failure, report
            onError: errors => {
                // show me
                console.log(`viz.controls.viz.useAutoValueController:`)
                console.group()
                console.log(`viewport ${viewport}:`)
                console.log(`ERROR while setting the auto flag of ${controller}`)
                console.log(`for channel ${channel}`)
                console.log(errors)
                console.groupEnd()
            },
        })
        // all done
        return
    }

    // all done
    return { setAuto }
}


// the mutation that sets the auto flag
export const useAutoValueControllerMutation = graphql`
mutation useAutoValueControllerMutation($input: ViewValueAutoSetInput!) {
    viewValueAutoSet(input: $input) {
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
