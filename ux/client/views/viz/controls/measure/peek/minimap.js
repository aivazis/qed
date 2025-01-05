// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2025 all rights reserved


// externals
import React from 'react'
import { graphql, useFragment } from 'react-relay/hooks'
import styled from 'styled-components'

// project
// shapes
import { Target } from '~/shapes'
// widgets
import { SVG } from '~/widgets'
// colors
import { theme } from "~/palette"


// local
// hooks
import { tileURI } from '~/views/viz'
// components
import { Down } from './down'
import { Left } from './left'
import { Right } from './right'
import { Up } from './up'


// a table of the points on the {measure} layer of the active viewport
export const Minimap = ({ viewport, view, point }) => {

    // unpack the view
    const { reader, dataset, channel, zoom, measure } = useFragment(
        minimapControlsGetMeasureLayerStateFragment, view
    )
    // form the base tile uri at zoom level 0, suitable for the minimap
    const uri = tileURI({
        viewport, reader, dataset, channel, zoom: { horizontal: 0, vertical: 0 }
    })

    // get the active dataset extent
    const { origin, shape } = dataset
    // get the anchor selection
    const { selection } = measure

    // we fetch a tile with shape
    const tile = [128, 128]
    // and origin that attempts to have our point at the center,
    // without crossing the raster boundary
    const anchor = point.map((p, idx) => {
        // the margin is half the tile extent
        const margin = tile[idx] / 2
        // if centering the tile at {point} crosses the leading edge of the raster
        if (p < origin[idx] + margin) {
            // move it
            return origin[idx]
        }
        // if centering the tile at {point} crosses the trailing edge of the raster
        if (p > shape[idx] - margin) {
            // move it
            return shape[idx] - 2 * margin
        }
        // otherwise, shift the coordinate by the margin and return it
        return p - margin
    })
    // now, compute how much we have to shift the target
    // the stretch comes from displaying a {tile} into a {256x256} box
    const delta = point.map((p, idx) => {
        // again, the margin is half the tile extent
        const margin = tile[idx] / 2
        // compute the incursion into the leading edge
        const lead = p - margin - origin[idx]
        // if this is negative
        if (lead < 0) {
            // stretch it and return it
            return 2 * lead
        }
        // compute the incursion into the trailing edge
        const trail = p + margin - shape[idx]
        // if its positive
        if (trail > 0) {
            // stretch it and return it
            return 2 * trail
        }
        // otherwise, no shift
        return 0
    })

    // derive the tile rep
    const rep = `${anchor[0]}x${anchor[1]}+${tile[0]}x${tile[1]}`
    // assemble the data request URI
    const base = [uri, rep].join("/")

    // style the {target} shape
    const target = {
        icon: {
            stroke: theme.page.viewportBorder,
            strokeWidth: "3",
        }
    }
    // and its placemat
    const placemat = {
        icon: {
            stroke: theme.page.relief,
            strokeWidth: "7",
            vectorEffect: "non-scaling-stroke",
        }
    }

    // deduce the magic anchor
    const handle = (selection.length > 0) ? selection[0] : null
    // build the displacement choices
    const deltas = [1, 5, 10, 50]

    // render
    return (
        <Box>
            <Data src={base} />
            <Map>
                <g transform={`translate(${delta[1]} ${delta[0]}) scale(${256 / 1000})`}>
                    {/* the marker, visible only when there are selected anchors */}
                    {selection.length > 0 && <Target style={placemat} />}
                    {selection.length > 0 && <Target style={target} />}
                    {/* verniers */}
                    <Up viewport={viewport} view={view} handle={handle} deltas={deltas} />
                    <Right viewport={viewport} view={view} handle={handle} deltas={deltas} />
                    <Down viewport={viewport} view={view} handle={handle} deltas={deltas} />
                    <Left viewport={viewport} view={view} handle={handle} deltas={deltas} />
                </g>
            </Map>
        </Box>
    )
}


// the container
const Box = styled.div`
    position: relative;
    width: 256px;
    height: 256px;
    background-color: ${() => theme.page.shaded};
    margin: 0.5rem auto;
    border: 1px solid ${() => theme.page.viewportBorder};
`

const Data = styled.img`
    width: 256px;
    height: 256px;
`

const Map = styled(SVG)`
    position: absolute;
    top: 0px;
    left: 0px;
    width: 256px;
    height: 256px;
`


// the fragment
const minimapControlsGetMeasureLayerStateFragment = graphql`
    fragment minimapControlsGetMeasureLayerStateFragment on View {
        reader {
            api
        }
        dataset {
            name
            origin
            shape
        }
        channel {
            tag
        }
        measure {
            selection
        }
        zoom {
            horizontal
            vertical
        }
    }
`


// end of file
