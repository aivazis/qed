// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
// relay
import { graphql, usePreloadedQuery, useQueryLoader } from 'react-relay/hooks'


// query preloader
export const useNicknameLoader = () => {
    // load the query
    const context = useQueryLoader(query)
    // and return the loading context
    return context
}

// use the preloaded query
export const useQueryNickname = (qref) => {
    // get the suggestion
    const { nickname } = usePreloadedQuery(query, qref)
    // and return it
    return nickname
}

// ask the server to suggest a name for the reader of the dataset at {uri}
const query = graphql`query useFetchNicknameQuery($archive: String!, $uri: String!) {
    nickname(archive: $archive, uri: $uri)
}`


// end of file
