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


// the values the server suggests for the setting {trait} of the factory {node} of the pipeline
// {diagram}: whether they are all it can take, and the values, each with the text that sets it and
// how it reads; nothing while they are on their way, or when there is nothing to ask about
export const useSuggestions = ({ diagram, node, trait }) => {
    // the answer, along with the setting it is about
    const [suggestions, setSuggestions] = React.useState(null)
    // ask whenever the question changes
    React.useEffect(() => {
        // with nothing to ask about
        if (!diagram || !node || !trait) {
            // there is no answer
            setSuggestions(null)
            // and nothing to clean up
            return
        }
        // whether the answer is still wanted
        let wanted = true
        // ask, every time, since the state of the factory may have changed since the last answer
        const request = fetchQuery(
            environment, query, { diagram, node, trait }, { fetchPolicy: "network-only" },
        ).subscribe({
            // when the answer arrives
            next: data => {
                // the suggestions, if any
                const found = data?.qed?.suggestions ?? null
                // keep them, if they are still wanted, marked with what they are about
                if (wanted) setSuggestions(found ? { node, trait, ...found } : null)
            },
            // if the question cannot be answered
            error: () => {
                // there is nothing to show
                if (wanted) setSuggestions(null)
            },
        })
        // when the question changes, or the field goes away
        return () => {
            // the answer is no longer wanted
            wanted = false
            // so stop asking
            request.unsubscribe()
        }
    }, [diagram, node, trait])
    // hand off the answer, but only the one about the setting asked about now
    return suggestions?.node === node && suggestions?.trait === trait ? suggestions : null
}


// the question
const query = graphql`
    query useSuggestionsQuery($diagram: ID!, $node: ID!, $trait: String!) {
        qed {
            suggestions(diagram: $diagram, node: $node, trait: $trait) {
                # whether they are all the values the setting can take
                closed
                # the values
                choices {
                    value
                    label
                }
            }
        }
    }
`


// end of file
