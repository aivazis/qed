// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'

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
    // ask it for all known data readers and attach them as read-only state
    const { readers } = useFragment(readersGetReadersFragment, qed)
    // render
    return (
        <>
            {/* the title of the panel */}
            <Header title="datasets" style={styles.header} >
                <Save />
            </Header>
            {/* go through the readers and render them */}
            {readers.map(reader => (
                <Reader key={reader.id} qed={qed} reader={reader} />
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
    }
`

// end of file
