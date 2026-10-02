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
// formatting
import { number } from './format'
// styles
import styles from './styles'


// the short names of the measures, in the order they are shown
const names = {
    once: "read alone",
    joint: "read together",
    alone: "chunks one at a time",
    fill_mean: "page fill",
    locality: "locality",
    empty: "nearly empty",
    unwritten: "never written",
    fill_chunks: "chunks of fill",
    compression: "compression",
    stored_mib: "stored, MiB",
    decode_ms: "decode fill, ms",
    encode_ms: "encode fill, ms",
}



// where the raster falls among the rasters of the census of its kind of product
export const Census = ({ census }) => {
    // the measures, by name
    const measures = Object.fromEntries(census.measures.map(measure => [measure.name, measure]))
    // the ones with a short name that this raster has, in order
    const shown = Object.keys(names).filter(name => measures[name]?.value != null)
    // the title
    const title = `${census.kind ?? "all"} rasters of ${census.product}, cycle ${census.cycle}: ${census.rasters}`

    // render
    return (
        <Tray title="census" initially={true} state="enabled" scale={0.5}>
            <Housing data-qed-region="quality-census">
                <Title>{title}</Title>
                <Table>
                    <thead>
                        <tr>
                            <Head />
                            <Head>this</Head>
                            <Head>census</Head>
                            <Head>median</Head>
                        </tr>
                    </thead>
                    <tbody>
                        {shown.map(name => {
                            // the measure
                            const measure = measures[name]
                            // render its row
                            return (
                                <tr key={name} data-qed-measure={name}>
                                    <Name title={measure.label}>{names[name]}</Name>
                                    <Value>{number(measure.value)}</Value>
                                    <Spark>
                                        <Histogram counts={measure.bins} width={120} height={24}
                                            domain={[measure.low, measure.high]} ticks={false}
                                            marker={{ value: measure.value, label: `this raster: ${number(measure.value)}` }}
                                            label={`${measure.label} over the census`}
                                        />
                                    </Spark>
                                    <Value>{number(measure.median)}</Value>
                                </tr>
                            )
                        })}
                    </tbody>
                </Table>
            </Housing>
        </Tray>
    )
}


// the housing
const Housing = styled.div`
    margin: 0.25rem 1.0rem 0.5rem 1.0rem;
    font-family: inconsolata;
    font-size: 90%;
    cursor: default;
`

// the title
const Title = styled.div`
    color: ${styles.dim};
    margin-bottom: 0.25rem;
`

// the table
const Table = styled.table`
    border-collapse: collapse;
`

// a column head
const Head = styled.th`
    color: ${styles.dim};
    font-weight: normal;
    text-align: left;
    padding: 0 0.5rem 0.1rem 0;
`

// the name of a measure
const Name = styled.td`
    color: ${styles.dim};
    padding: 0 0.75rem 0 0;
    white-space: nowrap;
`

// a value
const Value = styled.td`
    color: ${styles.normal};
    padding: 0 0.5rem 0 0;
    text-align: right;
`

// the sparkline
const Spark = styled.td`
    padding: 0 0.5rem 0 0;
    vertical-align: middle;
`


// end of file
