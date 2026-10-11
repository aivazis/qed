// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import { graphql, useMutation } from 'react-relay/hooks'


// change how every client looks at the playground: the projection of its diagram, and the trays
// of its panel that are open; the server tells the other clients, and the answer updates this one
export const usePlaygroundView = () => {
    // the two mutations
    const [commitProjection] = useMutation(usePlaygroundViewProjectionMutation)
    const [commitTray] = useMutation(usePlaygroundViewTrayMutation)
    // report a failure
    const complain = (what, errors) => {
        // show me
        console.log(`playground.usePlaygroundView:`)
        console.group()
        console.log(`ERROR while ${what}`)
        console.log(errors)
        console.groupEnd()
        // all done
        return
    }
    // project the diagram {kind}, turned by {azimuth} quarter turns, from {below} the floor or above
    const project = ({ kind, azimuth, below }) => {
        // send the request
        commitProjection({
            // the payload
            variables: { input: { kind, azimuth, below } },
            // on failure, report
            onError: errors => complain(`projecting the playground ${kind}`, errors),
        })
        // all done
        return
    }
    // open the tray called {name} when {expanded}, close it otherwise
    const tray = (name, expanded) => {
        // send the request
        commitTray({
            // the payload
            variables: { input: { tray: name, expanded } },
            // on failure, report
            onError: errors => complain(`${expanded ? "opening" : "closing"} the tray ${name}`, errors),
        })
        // all done
        return
    }
    // publish
    return { project, tray }
}


// the mutations; the responses carry the whole view, which replaces the one on screen
const usePlaygroundViewProjectionMutation = graphql`
    mutation usePlaygroundViewProjectionMutation($input: PlaygroundProjectionSetInput!) {
        playgroundProjectionSet(input: $input) {
            view { id kind azimuth below trays }
        }
    }
`

const usePlaygroundViewTrayMutation = graphql`
    mutation usePlaygroundViewTrayMutation($input: PlaygroundTraySetInput!) {
        playgroundTraySet(input: $input) {
            view { id kind azimuth below trays }
        }
    }
`


// end of file
