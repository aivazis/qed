// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
// relay
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'


// ask the server of known data sources
export const useFetchAllReaders = () => {
    // load the data sources
    const { readers } = useLazyLoadQuery(query)
    // and return them
    return readers
}


// query all known data sources
const query = graphql`query useFetchAllReadersQuery {
    readers {
        # the id of the reader
        id
        # its name of the reader
        name
        # plus whatever readers need to render themselves
        ...context_reader
    }
}`


// end of file
