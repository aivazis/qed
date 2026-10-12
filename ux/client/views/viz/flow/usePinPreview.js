// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, fetchQuery } from 'react-relay'

// project
// the relay environment
import { environment } from '~/environment'


// what pinning the factory {node} of the pipeline {diagram} to the class {family} would do, as
// the server works it out with the plan the pin itself carries out; nothing while it is on its way,
// when there is nothing to ask about, or when the pin cannot be made
export const usePinPreview = ({ diagram, node, family }) => {
    // the answer, along with the class it is about
    const [preview, setPreview] = React.useState(null)
    // ask whenever the question changes
    React.useEffect(() => {
        // with nothing to ask about
        if (!diagram || !node || !family) {
            // there is no answer
            setPreview(null)
            // and nothing to clean up
            return
        }
        // whether the answer is still wanted
        let wanted = true
        // ask, every time, since the diagram may have changed since the last answer
        const request = fetchQuery(
            environment, query, { diagram, node, family }, { fetchPolicy: "network-only" },
        ).subscribe({
            // when the answer arrives
            next: data => {
                // the preview, if the pin can be made
                const found = data?.qed?.pinPreview ?? null
                // keep it, if it is still wanted, marked with the class it is about
                if (wanted) setPreview(found ? { family, ...found } : null)
            },
            // if the question cannot be answered
            error: () => {
                // there is nothing to show
                if (wanted) setPreview(null)
            },
        })
        // when the question changes, or the preview goes away
        return () => {
            // the answer is no longer wanted
            wanted = false
            // so stop asking
            request.unsubscribe()
        }
    }, [diagram, node, family])
    // hand off the answer, but only the one about the class asked about now
    return preview?.family === family ? preview : null
}


// the question
const query = graphql`
    query usePinPreviewQuery($diagram: ID!, $node: ID!, $family: String!) {
        qed {
            pinPreview(diagram: $diagram, node: $node, family: $family) {
                # the label the factory would have
                label
                # the slots it would gain
                slots {
                    trait
                    input
                    output
                    at { x y z }
                }
                # the slots it would let go of
                dropped
            }
        }
    }
`


// end of file
