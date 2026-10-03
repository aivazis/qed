// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
// relay
import { fetchQuery, graphql, useRelayEnvironment } from 'react-relay'


// ask the server for a name for the reader of the dataset at {uri}, in the style of the product
// family in {module}; the answer carries either the name or the reason there is none
export const useFetchNickname = ({ archive, uri, module }) => {
    // get the current relay environment
    const environment = useRelayEnvironment()
    // the answer, tagged with the family it was asked for
    const [answer, setAnswer] = React.useState(null)
    // ask whenever the family changes
    React.useEffect(() => {
        // with no family, there is nothing to ask
        if (module === null) return
        // ask the server every time, since the names in use change as readers connect
        const options = { fetchPolicy: "network-only" }
        // send the query
        const subscription = fetchQuery(environment, query, { archive, uri, module }, options)
            .subscribe({
                // when the name arrives
                next: ({ nickname }) => {
                    // record it
                    setAnswer({ module, nickname, error: null })
                },
                // if the server cannot suggest one
                error: error => {
                    // record the reason, and leave the name for the user to type
                    setAnswer({ module, nickname: "", error: `${error}` })
                },
            })
        // an answer that arrives after the family has changed is of no use
        return () => subscription.unsubscribe()
    }, [archive, uri, module])
    // the answer for a family the user has moved away from would seed the form with the wrong
    // name, so it counts as no answer yet
    return answer?.module === module ? answer : null
}


// the suggestion
const query = graphql`query useFetchNicknameQuery(
    $archive: String!, $uri: String!, $module: String!
) {
    nickname(archive: $archive, uri: $uri, module: $module)
}`


// end of file
