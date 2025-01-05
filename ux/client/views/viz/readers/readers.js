// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
// router
import { useNavigate } from 'react-router-dom'

// project
// widgets
import { Header } from '~/widgets'

// locals
// components
import { Reader } from '../reader'
import { Save } from './save'
// styles
import styles from './styles'


// export the activity panel
export const Readers = ({ qed }) => {
    // ask the server side store for all known data readers and views
    const { readers, views } = useFragment(readersGetReadersFragment, qed)
    // get the navigation handler
    const navigate = useNavigate()
    // redirect
    React.useEffect(() => {
        // if there are no registered readers
        if (readers.length == 0) {
            // go to the archive page
            navigate("explore")
        }
        // all done
        return
    }, [readers])

    // render
    return (
        <>
            {/* the title of the panel */}
            <Header title="datasets" style={styles.header} >
                <Save />
            </Header>
            {/* go through the readers and render them */}
            {readers.map(reader => (
                <Reader key={reader.id} reader={reader} qed={qed} views={views} />
            ))}
        </>
    )
}

// the fragments
const readersGetReadersFragment = graphql`
    fragment readersGetReadersFragment on QED {
        readers {
            id
            # and whatever else readers need
            ...contextGetReaderFragment
        }
        views {
            ...vizGetScrollSyncedViewsFragment
            ...viewportViewerGetViewFragment
            ...contextReaderGetViewFragment
            ...measureViewerGetMeasureLayerStateFragment
            ...syncViewerGetScrollSyncStateFragment
            ...printViewerGetViewFragment
        }
    }
`

// end of file
