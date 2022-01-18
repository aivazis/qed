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
// components
import { Blank } from './blank'
import { Tab } from './tab'
// styles
import styles from './styles'


// export the data viewer
export const Viewer = ({ viewport, view, registrar }) => {
    // if my view is trivial
    if (!view) {
        // show a blank panel
        return <Blank />
    }
    // unpack it
    const { reader, dataset, channel } = view
    // and check again for the trivial cases
    if (!reader || !dataset || !channel) {
        // to show a blank panel
        return <Blank />
    }
    // extract some metadata
    const { uuid: readerUUID, uri, api } = reader
    const { uuid: datasetUUID, datatype, shape, origin, tile } = dataset

    // assemble the data request URI
    const base = [api, readerUUID, datasetUUID, channel].join("/")

    // mix my paint
    const paint = styles.viewer
    // and render
    return (
        <>
            {/* the title bar with the dataset description and the controls */}
            <Tab viewport={viewport} view={view} />

            {/* identifying metadata */}
            <Meta.Table style={paint}>
                <Meta.Entry attribute="uri" style={paint}>
                    {uri}
                </Meta.Entry>
                <Meta.Entry attribute="reader" style={paint}>
                    {readerUUID}
                </Meta.Entry>
                <Meta.Entry attribute="dataset" style={paint}>
                    {datasetUUID}
                </Meta.Entry>
                <Meta.Entry attribute="data" style={paint}>
                    {base}
                </Meta.Entry>
                <Meta.Entry attribute="type" style={paint}>
                    {datatype}
                </Meta.Entry>
                <Meta.Entry attribute="origin" style={paint}>
                    {origin.join(", ")}
                </Meta.Entry>
                <Meta.Entry attribute="shape" style={paint}>
                    {shape.join(" x ")}
                </Meta.Entry>
                <Meta.Entry attribute="tile" style={paint}>
                    {tile.join(" x ")}
                </Meta.Entry>
            </Meta.Table>
        </>
    )

    // nothing yet
    return null
}


// end of file
