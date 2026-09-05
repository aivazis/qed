// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// turn a journal channel on or off
export const useSetChannel = () => {
    // flipping the flag mutates the server's journal
    const [commit, pending] = useMutation(journalChannelSetMutation)

    // make the handler
    const setActive = ({ severity, name, active }) => {
        // if there is a pending operation
        if (pending) {
            // nothing to do
            return
        }
        // otherwise, send the mutation to the server; the payload carries the channel with its
        // new state, which the relay store folds into the listing by id
        commit({
            // the payload
            variables: {
                input: { severity, name, active },
            },
            // on failure, report
            onError: errors => {
                // show me
                console.log(`viz.console.useSetChannel:`)
                console.group()
                console.log(`ERROR while setting the active flag of ${severity} ${name}`)
                console.log(errors)
                console.groupEnd()
            },
        })
        // all done
        return
    }

    // all done
    return { setActive }
}


// the mutation; exported so the {window.qed} automation facade can commit it against the live
// store exactly as this hook does
export const journalChannelSetMutation = graphql`
    mutation useSetChannelMutation($input: JournalChannelSetInput!) {
        journalChannelSet(input: $input) {
            channel {
                id
                severity
                name
                active
                fatal
            }
        }
    }
`


// end of file
