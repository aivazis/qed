// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// shapes
import { Target } from '~/shapes'
// widgets
import { SVG } from '~/widgets'

// local
// hooks
import { useViews } from '../../viz/useViews'
import { usePixelPathSelection } from '../../viz/usePixelPathSelection'
// components
import { Down } from './down'
import { Left } from './left'
import { Right } from './right'
import { Up } from './up'



// a table of the points on the {measure} layer of the active viewport
export const Minimap = ({ path }) => {
    // get the node selection
    const selection = usePixelPathSelection()
    // get the {activeViewport} and the set of {views} from {viz}
    const { views, activeViewport } = useViews()

    // if the selection does not contain precisely one element
    if (selection.size !== 1) {
        // bail
        return null
    }
    // get the node
    const node = [...selection][0]

    // unpack the view associated with the active viewport
    const { reader, dataset, channel } = views[activeViewport]
    // check for the trivial cases
    if (!reader || !dataset || !channel) {
        // bail
        return null
    }
    // otherwise, unpack the view
    const { uuid: readerUUID, api } = reader
    const { uuid: datasetUUID, origin, shape } = dataset

    // get the point of interest
    const point = path[node]
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
    const base = [api, readerUUID, datasetUUID, channel, 0, rep].join("/")

    // style the {target} shape
    const style = {
        icon: {
            stroke: "hsl(28deg, 90%, 45%)",
            strokeWidth: "3",
        }
    }

    // render
    return (
        <Box>
            <Data src={base} />
            <Map>
                <g transform={`translate(${delta[1]} ${delta[0]}) scale(${256 / 1000})`}>
                    {/* the marker */}
                    <Target style={style} />
                    {/* verniers */}
                    <Up node={node} />
                    <Right node={node} />
                    <Down node={node} />
                    <Left node={node} />
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
    background-color: hsl(0deg, 0%, 10%);
    margin: 0.0rem 1.0rem 1.0rem 1.0rem;
    border: 2px solid hsl(28deg, 30%, 25%);
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


// end of file
