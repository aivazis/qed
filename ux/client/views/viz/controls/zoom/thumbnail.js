// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// externals
import React from 'react'
import styled from 'styled-components'

// project
// hooks
import { tileURI } from '~/views/viz'


// the dataset thumbnail: a small mosaic of heavily decimated tiles from the {data} api that
// covers the gray placeholder once every slice has arrived; the same render pass seeds the
// server side dataset statistics, so the reveal marks the end of the collection
export const Thumbnail = ({ viewport, reader, dataset, channel, session, shape, scale, ils }) => {
    // the generation currently on display; starts out empty, which leaves the gray placeholder
    // visible while the first generation is being fetched
    const [current, setCurrent] = React.useState(null)
    // the load ledger of the generation being fetched
    const progress = React.useRef({ key: null, loaded: null })
    // the retry round: bumping it remounts the slices that haven't arrived, so a dropped
    // connection or a lost load event delays the reveal instead of canceling it
    const [round, setRound] = React.useState(0)

    // the thumbnail can only be formed when the view is fully resolved
    const live = (reader && dataset && channel && session) ? true : false

    // assemble the specification of the desired generation
    const spec = React.useMemo(() => {
        // if the view is not fully resolved
        if (!live) {
            // there is nothing to fetch
            return null
        }
        // unpack the dataset shape
        const [dHeight, dWidth] = shape
        // pick the decimation level that brings the long axis down to a few thousand pixels;
        // the browser resizes the result into the minimap box, so the extra resolution costs
        // nothing on screen, while the render decomposes into many standard slices that keep
        // the whole crew busy and sample the raster densely enough to seed useful statistics
        const exp = Math.max(0, Math.trunc(Math.log2(Math.max(dHeight, dWidth) / resolution)))
        // deduce the corresponding stride
        const stride = 2 ** exp
        // form the decimated raster shape; floor division, so the footprint stays within bounds
        const decimated = [Math.trunc(dHeight / stride), Math.trunc(dWidth / stride)]
        // form the base uri of tile requests at this decimation level
        const base = tileURI({
            viewport, reader, dataset, channel,
            zoom: { horizontal: -exp, vertical: -exp },
        })
        // the slice unit is the dataset's preferred tile: the HDF5 chunk shape for products
        // that have one, so slice footprints stay chunk-aligned and no chunk is decompressed
        // by two different workers
        const unit = dataset.tile ?? [512, 512]
        // make a pile for the tile specs
        const tiles = []
        // chop the decimated raster into slices, matching the crew's unit of work,
        // by going through the vertical partition
        for (const [row, height] of partition(decimated[0], unit[0])) {
            // and the horizontal partition
            for (const [col, width] of partition(decimated[1], unit[1])) {
                // form the request for this slice; the session token busts the browser cache
                // whenever the server rolls it, e.g. on a change to the visualization stretch
                const uri = `${base}/${row}x${col}+${height}x${width}?session=${session}`
                // record the slice; its placement is in decimated coordinates so the geometry
                // can be projected onto the minimap at render time with the live {scale}
                tiles.push({ uri, row, col, height, width })
            }
        }
        // a generation is identified by its base uri and the session token
        return { key: `${base}?session=${session}`, stride, decimated, tiles }
        // the {scale} is deliberately not an input: it affects placement, not identity
    }, [live, viewport, reader, dataset, channel, session, shape])

    // when the desired generation is new, reset the ledger; this happens during render, but it
    // is idempotent because it is gated by the generation key
    if (spec && progress.current.key !== spec.key && (!current || current.key !== spec.key)) {
        // start a fresh ledger
        progress.current = { key: spec.key, loaded: new Set() }
        // and grant the new generation a full allowance of retries; a render-phase state
        // update, the sanctioned way to reset state derived from changing inputs
        setRound(0)
    }

    // deduce whether a new generation is in flight
    const pending = spec && (!current || current.key !== spec.key)

    // fetch the pending generation: slices are preloaded with detached {Image} objects, whose
    // load events are reliable, unlike those of svg {image} elements; once every slice is in
    // the browser cache the generation goes on display and the svg mosaic paints instantly
    React.useEffect(() => {
        // if nothing is in flight
        if (!pending) {
            // nothing to fetch
            return undefined
        }
        // capture the generation this effect serves
        const generation = spec
        // and its ledger
        const ledger = progress.current
        // the teardown guard
        let alive = true
        // go through the slices
        for (const tile of generation.tiles) {
            // skip the ones that have already arrived
            if (ledger.loaded.has(tile.uri)) {
                // on to the next one
                continue
            }
            // make a loader
            const img = new window.Image()
            // record the arrival of its slice
            img.onload = () => {
                // unless the generation is stale
                if (!alive || ledger !== progress.current) {
                    // in which case, ignore it
                    return
                }
                // add the slice to the ledger
                ledger.loaded.add(tile.uri)
                // if the generation is now complete
                if (ledger.loaded.size === generation.tiles.length) {
                    // put it on display
                    setCurrent(generation)
                }
                // all done
                return
            }
            // failures are left to the retry rounds
            img.onerror = () => null
            // start the fetch
            img.src = tile.uri
        }
        // register the teardown
        return () => { alive = false }
        // refetch the stragglers whenever the generation changes or a retry round starts
    }, [pending, spec?.key, round])

    // while a generation is in flight, nudge it periodically: refetching the slices that
    // haven't arrived retries dropped connections; completed slices sit in the server cache,
    // so a retry is cheap. the round cap turns a persistently broken generation into a quiet
    // fallback to whatever is on display
    React.useEffect(() => {
        // if nothing is in flight
        if (!pending) {
            // nothing to watch
            return undefined
        }
        // otherwise, arm the timer
        const timer = window.setInterval(() => {
            // advance the round, up to the cap
            setRound(old => old < retries ? old + 1 : old)
        }, patience)
        // and register its teardown
        return () => window.clearInterval(timer)
        // rearm whenever the pending generation changes identity or resolves
    }, [pending, spec?.key])

    // project a slice onto the minimap: decimated coordinates back to source pixels, then
    // through the minimap scale; interior slices bleed one screen pixel into their trailing
    // neighbors, which paint over the overlap, so fractional placement leaves no seams
    const place = (tile, generation) => {
        // unpack the generation geometry
        const { stride, decimated } = generation
        // one screen pixel, in minimap units
        const bleed = 1 / ils
        // and project
        return {
            x: tile.col * stride * scale,
            y: tile.row * stride * scale,
            width: tile.width * stride * scale
                + (tile.col + tile.width < decimated[1] ? bleed : 0),
            height: tile.height * stride * scale
                + (tile.row + tile.height < decimated[0] ? bleed : 0),
        }
    }

    // if the view is not fully resolved
    if (!live) {
        // leave the placeholder alone
        return null
    }
    // render; only the completed generation appears, painted from the browser cache, so the
    // gray placeholder shows through until the crew is done; the thumbnail is decorative and
    // must not intercept the minimap interactions
    return (
        <Mat aria-hidden="true" data-qed-thumbnail={current ? "ready" : "pending"}>
            {current && current.tiles.map(tile => (
                <Sliver key={tile.uri} href={tile.uri} {...place(tile, current)}
                    preserveAspectRatio="none" />
            ))}
        </Mat>
    )
}


// the target long-axis extent of the decimated thumbnail; a few thousand pixels, so the crew
// has a real workload of slices while the browser shrinks the mosaic into the minimap box
const resolution = 2048
// the pause between retry rounds, generous enough that a slice legitimately in flight on a
// cold source is left alone
const patience = 30000
// the retry allowance per generation
const retries = 5


// helpers
// given an {extent}, generate (start, chunk) pairs that cover it with {tile} sized chunks,
// plus whatever remainder is left over
function* partition(extent, tile) {
    // figure out how many whole chunks fit
    const div = Math.trunc(extent / tile)
    // and what's left behind
    const mod = extent % tile
    // the first {div} entries are
    for (let i = 0; i < div; ++i) {
        // whole chunks at multiples of {tile}
        yield [i * tile, tile]
    }
    // if there is anything left over
    if (mod > 0) {
        // it forms the trailing chunk
        yield [div * tile, mod]
    }
    // all done
    return
}


// styling
// the group; transparent to pointer events so clicks fall through to the gray hit target
const Mat = styled.g`
    pointer-events: none;
`

// the individual slices
const Sliver = styled.image`
    pointer-events: none;
`


// end of file
