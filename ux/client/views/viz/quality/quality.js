// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// widgets
import { Header } from '~/widgets'

// locals
// hooks
import { useViewports } from '../viz/useViewports'
// components
import { Layout } from './layout'
// styles
import styles from './styles'


// the panel that shows how the dataset in the active viewport sits in its file
export const Quality = ({ qed }) => {
    // the active viewport
    const { activeViewport } = useViewports()
    // unpack the views
    const { views } = useFragment(qualityGetDatasetInViewFragment, qed)
    // the dataset in the active view, if any
    const dataset = views[activeViewport]?.dataset?.name ?? null

    // render
    return (
        <Panel data-qed-panel="quality">
            {/* the title of the panel */}
            <Header title="quality" style={styles.header} />
            {/* without a dataset, there is nothing to describe */}
            {dataset === null && <Note>select a dataset to see how it sits in its file</Note>}
            {/* otherwise, describe it; the first description reads the file, so it takes a while */}
            {dataset !== null &&
                <React.Suspense fallback={<Note>reading the layout of the file...</Note>}>
                    <Layout dataset={dataset} />
                </React.Suspense>
            }
        </Panel>
    )
}


// the container
const Panel = styled.div`
    display: flex;
    flex-direction: column;
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
`

// a note in place of the contents
const Note = styled.div`
    font-family: inconsolata;
    font-size: 90%;
    cursor: default;
    padding: 0.5rem 1.0rem;
    color: ${styles.dim};
`


// the fragment: the name of the dataset in each view
const qualityGetDatasetInViewFragment = graphql`
    fragment qualityGetDatasetInViewFragment on QED {
        views {
            dataset {
                name
            }
        }
    }
`


// end of file
