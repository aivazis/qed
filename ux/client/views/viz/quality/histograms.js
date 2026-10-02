// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// widgets
import { Histogram, Tray } from '~/widgets'

// locals
// styles
import styles from './styles'


// the distributions of the chunk sizes and of the fill of the pages
export const Histograms = ({ layout }) => {
    // unpack
    const { summary } = layout
    // render
    return (
        <Tray title="histograms" initially={true} state="enabled" scale={0.5}>
            <Housing>
                <Title>stored size of a chunk, as a share of its raw size</Title>
                <Histogram counts={summary.sizes} width={360} height={100} log={true} unit="chunks"
                    label="stored size of a chunk as a share of its raw size" />
                {summary.fill &&
                    <>
                        <Title>share of each page the raster fills</Title>
                        <Histogram counts={summary.fill} width={360} height={100} log={true} unit="pages"
                            label="share of each page the raster fills" />
                    </>
                }
            </Housing>
        </Tray>
    )
}


// the housing
const Housing = styled.div`
    margin: 0.25rem 1.0rem 0.5rem 1.0rem;
`

// the title of a histogram
const Title = styled.div`
    font-family: inconsolata;
    font-size: 90%;
    cursor: default;
    color: ${styles.dim};
    margin: 0.25rem 0;
`


// end of file
