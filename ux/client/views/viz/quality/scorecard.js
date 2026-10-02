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
import { Tray } from '~/widgets'

// locals
// formatting
import { bytes, number, percent } from './format'
// styles
import styles from './styles'


// the numbers that describe the layout of a raster
export const Scorecard = ({ layout }) => {
    // unpack
    const { summary, fill } = layout
    // the rows: the storage, the pages, and the fill
    const rows = [
        ["storage", `${layout.shape.join(" x ")} ${layout.cell}, chunks of ${layout.tile.join(" x ")}`],
        ["filters", layout.filters.join(" > ") || "none"],
        ["file", layout.pageSize > 0
            ? `${layout.strategy}, pages of ${bytes(layout.pageSize)}, ${bytes(layout.fileBytes)}`
            : `not paged, ${bytes(layout.fileBytes)}`],
        ["chunks written", `${summary.written} of ${summary.grid}`],
        ["stored", `${bytes(summary.stored)}, compressed ${number(summary.compression)}x`],
        ["nearly empty", `${summary.empty} (${percent(summary.written ? summary.empty / summary.written : null)}), ${bytes(summary.emptyStored)}`],
        ["read alone", layout.pageSize > 0 ? `${number(summary.once)}x the bytes stored` : "-"],
        ["read together", layout.pageSize > 0 ? `${number(summary.joint)}x` : "-"],
        ["chunks one at a time", layout.pageSize > 0 ? `${number(summary.alone)}x` : "-"],
        ["page fill", percent(summary.fillMean)],
        ["locality", percent(summary.locality)],
    ]
    // and the fill
    const fills = [
        ["library fill", `${fill.hdf5 ?? "-"} (${fill.status})`],
        ["_FillValue", fill.cf ?? "none"],
        ["empty chunks hold", fill.holds ?? "-"],
        ["chunks of fill", fill.chunks === null ? "-" : `${fill.chunks}, ${bytes(fill.bytes)}`],
        ["decode one", fill.decodeMs === null ? "-" : `${number(fill.decodeMs)} ms, vs ${number(fill.makeMs)} ms to make`],
        ["encode one", fill.encodeMs === null ? "-" : `${number(fill.encodeMs)} ms at deflate level ${fill.level}`],
    ]
    // the verdict on the fill
    const verdict = fill.agrees === null ? null : fill.agrees ? "agrees" : "differs"

    // render
    return (
        <Tray title="layout" initially={true} state="enabled" scale={0.5}>
            <Table data-qed-region="quality-scorecard">
                <tbody>
                    {rows.map(([name, value]) => (
                        <tr key={name} data-qed-measure={name}>
                            <Name>{name}</Name>
                            <Value>{value}</Value>
                        </tr>
                    ))}
                    {/* a gap between the layout and the fill */}
                    <tr aria-hidden="true"><Gap colSpan={2} /></tr>
                    {fills.map(([name, value]) => (
                        <tr key={name} data-qed-measure={name}>
                            <Name>{name}</Name>
                            <Value>{value}</Value>
                        </tr>
                    ))}
                    {verdict !== null &&
                        <tr data-qed-measure="fill agrees">
                            <Name>declared fill</Name>
                            <Verdict data-qed-value={verdict} $agrees={fill.agrees}>{verdict}</Verdict>
                        </tr>
                    }
                </tbody>
            </Table>
        </Tray>
    )
}


// the table
const Table = styled.table`
    font-family: inconsolata;
    font-size: 90%;
    cursor: default;
    margin: 0.25rem 1.0rem 0.5rem 1.0rem;
    border-collapse: collapse;
`

// the name of a measure
const Name = styled.td`
    color: ${styles.dim};
    padding: 0.1rem 1.0rem 0.1rem 0;
    white-space: nowrap;
    vertical-align: top;
`

// its value
const Value = styled.td`
    color: ${styles.normal};
    padding: 0.1rem 0;
`

// the gap between the layout and the fill
const Gap = styled.td`
    height: 0.5rem;
`

// the verdict on the fill
const Verdict = styled.td`
    padding: 0.1rem 0;
    color: ${props => props.$agrees ? styles.normal : styles.danger};
`


// end of file
