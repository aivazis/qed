// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'

// project
// widgets
import { Meta } from '~/widgets'

// locals
// hooks
import { useGetTileURI } from '../viz/useGetTileURI'
import { useGetZoomLevel } from '../viz/useGetZoomLevel'
// components
import { Blank } from './blank'
import { Tab } from './tab'
import { Viewport } from './viewport'
// styles
import styles from './styles'


// export the data viewer
export const Viewer = ({ viewport, view, registrar }) => {
    // get the viewport zoom level
    const zoom = Math.trunc(useGetZoomLevel(viewport))
    // assemble the data request URI
    const base = useGetTileURI(viewport)

    // unpack the view
    const { reader, dataset, channel } = view
    // check for the trivial cases
    if (!reader || !dataset || !channel) {
        // to show a blank panel
        return (
            <>
                <Tab viewport={viewport} view={null} />
                <Blank />
            </>
        )
    }

    // otherwise, unpack the view
    const { uuid: readerUUID, id, uri } = reader
    const { uuid: datasetUUID, datatype, shape, origin, tile } = dataset

    // scale the shape to the current zoom level
    const effectiveShape = shape.map(s => Math.trunc(s / (2 ** zoom)))

    // mix my paint
    const paint = styles.viewer
    // and render
    return (
        <>
            {/* the title bar with the dataset description and the controls */}
            <Tab viewport={viewport} view={view} />

            {/* identifying metadata; most of it is debugging information */}
            <Meta.Table min={0} initial={0} max={5} style={paint}>
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
                    {readerUUID}
                </Meta.Entry>
                <Meta.Entry threshold={4} attribute="dataset" style={paint}>
                    {datasetUUID}
                </Meta.Entry>
                <Meta.Entry threshold={5} attribute="data" style={paint}>
                    {base}
                </Meta.Entry>
            </Meta.Table>

            {/* the viewport */}
            <Viewport viewport={viewport} view={view} registrar={registrar} />
        </>
    )
}


// end of file
