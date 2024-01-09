// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Meta } from '~/widgets'

// locals
// hooks
import { useGetTileURI } from '../viz/useGetTileURI'
import { useGetZoomLevel } from '../viz/useGetZoomLevel'
// styles
import styles from './styles'


// export the data viewer
export const Info = ({ viewport, view }) => {
    // get the viewport zoom level
    const zoom = Math.trunc(useGetZoomLevel(viewport))
    // assemble the data request URI
    const base = useGetTileURI({ viewport })

    // unpack the view
    const { reader, dataset } = view
    // extract the relevant metadata
    const { name: readerName, id, uri } = reader
    const { name: datasetName, datatype, shape, origin, tile } = dataset

    // scale the shape to the current zoom level
    const effectiveShape = shape.map(s => Math.trunc(s / (2 ** zoom)))

    // mix my paint
    const paint = styles.viewer
    // and render
    return (
        < Meta.Table min={0} initial={0} max={5} style={paint} >
            <Meta.Entry threshold={1} attribute="uri" style={paint}>
                {uri}
            </Meta.Entry>
            <Meta.Entry threshold={2} attribute="shape" style={paint}>
                {shape.join(" x ")}
            </Meta.Entry>
            <Meta.Entry threshold={2} attribute="zoom level" style={paint}>
                {zoom}
            </Meta.Entry>
            <Meta.Entry threshold={2} attribute="effective shape" style={paint}>
                {effectiveShape.join(" x ")}
            </Meta.Entry>
            <Meta.Entry threshold={3} attribute="tile" style={paint}>
                {tile.join(" x ")}
            </Meta.Entry>
            <Meta.Entry threshold={3} attribute="origin" style={paint}>
                {origin.join(", ")}
            </Meta.Entry>
            <Meta.Entry threshold={3} attribute="reader" style={paint}>
                {id}
            </Meta.Entry>
            <Meta.Entry threshold={3} attribute="type" style={paint}>
                {datatype}
            </Meta.Entry>
            <Meta.Entry threshold={4} attribute="reader" style={paint}>
                {readerName}
            </Meta.Entry>
            <Meta.Entry threshold={4} attribute="dataset" style={paint}>
                {datasetName}
            </Meta.Entry>
            <Meta.Entry threshold={5} attribute="data" style={paint}>
                {base}
            </Meta.Entry>
        </Meta.Table>
    )
}


// end of file
