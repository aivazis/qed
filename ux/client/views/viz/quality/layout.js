// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// locals
// hooks
import { useLayout } from './useLayout'
// components
import { Census } from './census'
import { Chunks } from './chunks'
import { FileMap } from './filemap'
import { Histograms } from './histograms'
import { Pages } from './pages'
import { Scorecard } from './scorecard'
// styles
import styles from './styles'


// the description of how {dataset} sits in its file
export const Layout = ({ dataset }) => {
    // get the layout
    const layout = useLayout(dataset)
    // the page in focus, which the chunk map, the page strip, and the file map share: hovering a
    // chunk puts its page in focus, and hovering a page puts it there directly
    const [focus, setFocus] = React.useState(null)
    // a product that is not an HDF5 file has none
    if (layout === null) {
        // so say so
        return <Note>{dataset} is not stored in an HDF5 file, so there is no layout to show</Note>
    }
    // render
    return (
        <>
            <Scorecard layout={layout} />
            {layout.census && <Census census={layout.census} />}
            <Chunks layout={layout} focus={focus} setFocus={setFocus} />
            {layout.strip && <Pages layout={layout} focus={focus} setFocus={setFocus} />}
            {layout.filemap && <FileMap layout={layout} focus={focus} setFocus={setFocus} />}
            <Histograms layout={layout} />
        </>
    )
}


// a note in place of the contents
const Note = styled.div`
    font-family: inconsolata;
    font-size: 90%;
    cursor: default;
    padding: 0.5rem 1.0rem;
    color: ${styles.dim};
`


// end of file
