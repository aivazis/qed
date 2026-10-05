// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
// relay
import { graphql, useLazyLoadQuery } from 'react-relay/hooks'


// get the session manager
export const useFetchQED = () => {
    // ask for the session manager
    const { qed } = useLazyLoadQuery(
        // the query
        query,
        // the vars
        {},
        // the options
        { fetchPolicy: "network-only" }
    )
    // and return it
    return qed
}


// the compiled operation is exported so the live-sync layer can refetch it imperatively
export const query = graphql`
    query useFetchQEDQuery {
        qed {
            # the server side store id
            id
            # the connected data archives
            ...context_archives
            # reader information for populating the panel of datasets
            ...readersGetReadersFragment
            # reader lifecycle information for the staging trigger
            ...vizStageReadersFragment
            # reader information for disconnecting readers from the panel
            ...disconnectReaderViewsFragment
            # for the panel of controls
            ...controlsGetDatasetAndChannelInViewFragment
            # information for rendering the viewport
            ...vizGetViewsFragment
            # for the sync control
            ...bodyGetSyncTableFragment
            # for the channel listing in the journal console
            ...channelsGetJournalFragment
            # for the dataset the quality panel describes
            ...qualityGetDatasetInViewFragment
            # for the activities that need a dataset in the active view
            ...activityBarGetViewsFragment
            # for the description of the node picked on the pipeline diagram
            ...nodesGetDiagramFragment
            # for the pipeline playground
            ...playgroundGetDiagramFragment
        }
    }
`


// end of file
