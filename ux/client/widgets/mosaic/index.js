// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'
import zip from 'lodash/zip'

// project
// widgets
import { Tile } from '~/widgets'


// a large raster represented as a rectangular grid of tiles
export const Mosaic = ({ uri, shape, origin, tile, session }) => {
    // render
    return (
        <Box shape={shape}>
            {mosaic(shape, origin, tile).map(spec => {
                // unpack
                const [origin, extent] = spec
                // form the uri
                const tileURI = `${uri}/${origin.join("x")}+${extent.join("x")}?session=${session}`
                // render
                return (
                    <Tile key={origin} uri={tileURI} shape={extent} />
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
    width: ${props => props.shape[1]}px;
    height: ${props => props.shape[0]}px;
`


// end of file
