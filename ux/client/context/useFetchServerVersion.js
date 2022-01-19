// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
// relay
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'


// ask the server of known data sources
export const useFetchServerVersion = () => {
    // load the version
    const { version } = useLazyLoadQuery(query)
    // and return it
    return version
}


// query all known data sources
const query = graphql`query useFetchServerVersionQuery {
    version {
        major
        minor
        micro
        revision
    }
}`


// end of file
