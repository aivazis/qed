// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// export the view
export { Viewer } from './viewer'

// tile URIs
// {api} names the route the tiles come from; it defaults to the one the reader publishes,
// and callers whose tiles are one-offs ask for a route that keeps them off the crews and
// out of the tile cache
export const tileURI = ({ viewport, reader, dataset, channel, zoom, api = null }) => {
    // unpack the zoom level
    const level = [-zoom.vertical, -zoom.horizontal]
    // normalize and build the tag
    const tag = level.map(z => Math.trunc(Math.max(z, 0))).join("x")
    // assemble the uri
    const uri = [api ?? reader.api, viewport, dataset.name, channel.tag, tag].join("/")
    // and return it
    return uri
}


// end of file
