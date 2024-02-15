// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
// relay
import { graphql, useLazyLoadQuery, usePreloadedQuery, useQueryLoader } from 'react-relay/hooks'


// fetch the contents of a directory lazily
export const useFetchShapeGuesses = (path) => {
    // get the contents
    const data = useLazyLoadQuery(
        // the query
        query,
        // the vars
        { path, },
        // the options
        { fetchPolicy: "network-only" }
    )
    // and return them
    return data
}

// query preloader
export const useShapeGuessesLoader = () => {
    // load the query
    const context = useQueryLoader(query)
    // and return the loading context
    return context
}

// use the preloaded query
export const useQueryShapeGuesses = (qref) => {
    // get the data
    const { guessShape: guesses } = usePreloadedQuery(query, qref)
    // and return it
    return guesses
}

// query the contents of the directory at {uri}
const query = graphql`query useFetchShapeGuessesQuery(
    $size: String!, $aspect: String!
) {
    guessShape(size: $size, aspect: $aspect) {
        lines
        samples
    }
}`


// end of file