// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { fetchQuery, graphql, useRelayEnvironment } from 'react-relay'


// ask the server for a nickname for an archive of the kind {type} at {uri}, or of the granules of
// {collection}; a form with nothing to go on yet leaves {uri} empty, and one that reconfigures an
// archive passes its {current} name, which is the archive's own to keep; the answer is the empty
// string until the server has one
export const useFetchArchiveNickname = ({ type, uri, collection = null, current = null }) => {
    // get the current relay environment
    const environment = useRelayEnvironment()
    // the suggestion
    const [nickname, setNickname] = React.useState("")
    // ask whenever the location changes
    React.useEffect(() => {
        // a form that has nothing to go on yet asks for nothing
        if (!uri) {
            // and has no suggestion
            setNickname("")
            // all done
            return
        }
        // the subscription to the answer, once the question goes out
        let subscription = null
        // wait for the user to pause, since the location changes with every keystroke
        const timer = setTimeout(() => {
            // ask the server every time, since the names in use change as archives connect
            const options = { fetchPolicy: "network-only" }
            // the question, with the name the archive has, if it has one
            const variables = { type, uri, collection, archive: current }
            // send the query
            subscription = fetchQuery(environment, query, variables, options)
                .subscribe({
                    // when the name arrives
                    next: ({ archiveNickname }) => {
                        // record it
                        setNickname(archiveNickname)
                    },
                    // if the server cannot suggest one
                    error: () => {
                        // leave the name for the user to type
                        setNickname("")
                    },
                })
        }, pause)
        // an answer for a location the user has moved away from is of no use
        return () => {
            // so don't ask
            clearTimeout(timer)
            // and don't listen
            subscription?.unsubscribe()
        }
    }, [type, uri, collection, current])
    // hand off the suggestion
    return nickname
}


// how long the user must stop typing before the question goes out, in milliseconds
const pause = 250

// the question
const query = graphql`query useFetchArchiveNicknameQuery(
    $type: String!, $uri: String!, $collection: String, $archive: String
) {
    archiveNickname(type: $type, uri: $uri, collection: $collection, archive: $archive)
}`


// end of file
