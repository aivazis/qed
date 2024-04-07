// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'
import zip from 'lodash/zip'

// project
// widgets
import { Tile } from '~/widgets'


// a large raster represented as a rectangular grid of tiles
export const Mosaic = ({ uri, origin, shape, tile, zoom, session }) => {
    // split the zoom level into two parts:
    // - magnification: the integer part of the zoom level
    // - distortion: the fractional part of the zoom level
    const magnification = zoom.map(level => 2 ** -((level > 0) ? 0 : Math.trunc(level)))
    const distortion = zoom.map(level => 2 ** -(level > 0 ? level : level - Math.trunc(level)))

    // compute the zoomed shape using only the magnification
    const magShape = shape.map((s, idx) => Math.trunc(s / magnification[idx]))
    // build the tiles
    const tiles = mosaic(magShape, origin, tile)
    // compute the zoomed shape taking into account the entire zoom level
    const zoomedShape = tiles.reduce(
        // the reducer
        (shape, tile) => {
            // unpack
            const [[y, x], [height, width]] = tile
            // we only care about the first row
            if (y == 0) {
                // distort and accumulate
                shape["width"] += Math.trunc(width / distortion[1])
            }
            // and the first column
            if (x == 0) {
                // distort and accumulate
                shape.height += Math.trunc(height / distortion[0])
            }
            // all done
            return shape
        },
        // initial value
        { height: 0, width: 0 }
    )

    // render
    return (
        <Box shape={zoomedShape}>
            {tiles.map(spec => {
                // unpack
                const [origin, shape] = spec
                // distort the shape
                const distorted = shape.map((s, idx) => Math.trunc(s / distortion[idx]))
                // form the uri
                const tileURI = `${uri}/${origin.join("x")}+${shape.join("x")}?session=${session}`
                // render
                return (
                    <Tile key={origin} uri={tileURI} shape={distorted} />
                )
            })}
        </Box>
    )
}


// helpers
// form a grid of mostly {tile} chunks that cover {shape}
function mosaic(shape, origin, tile) {
    // form (origin, tile) pairs
    const specs = cartesian(
        ...zip(origin, shape, tile).map(pair => Array.from(partition(...pair)))
    ).map(p => zip(...p))

    // and return them
    return specs
}

// form the cartesian product of n arrays
const cartesian = (first, ...rest) => rest.reduce(
    // given the partial result in {prefix} and the {current} array
    (prefix, current) => prefix.flatMap(
        // replace each entry in {prefix} with an array
        prefixEntry => current.map(
            // formed by splicing every entry of {current} into every entry of {prefix}
            argEntry => [prefixEntry, argEntry]
        )
    ),
    // starting with the first entry
    first
)

// given a {shape} and a {tile}, generate an array of pairs of (starting index, chunk) that
// partition {shape} into chunks
function* partition(origin, shape, tile) {
    // figure out how many times {tile} fits in {shape}
    const div = Math.trunc(shape / tile)
    // and what's left behind
    const mod = shape % tile

    // so, the first {div} entries are
    for (let i = 0; i < div; ++i) {
        // chunks of length {tile} at a multiple of {tile}
        yield [origin + i * tile, tile]
    }
    // and if there is anything left over
    if (mod > 0) {
        // it must be of length {mod} from the last multiple of {tile} that fits in {shape}
        yield [origin + div * tile, mod]
    }

    // all done
    return
}


// styles
// the container
const Box = styled.div`
    /* this must be sized by the client based on the raster shape */
    overflow: hidden;   /* hide anything that sticks out */

    /* let {flex} position my children */
    display: flex;
    /* a list of tiles that get wrapped based on their size */
    flex-direction: row;
    flex-wrap: wrap;

    /* extent */
    width: ${props => props.shape.width}px;
    height: ${props => props.shape.height}px;
`


// end of file
