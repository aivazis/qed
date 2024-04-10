// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// export the view
export { Viewer } from './viewer'

// tile URIs
export const tileURI = ({ viewport, reader, dataset, channel, zoom }) => {
    // unpack the zoom level
    const level = [-zoom.vertical, -zoom.horizontal]
    // normalize and build the tag
    const tag = level.map(z => Math.trunc(Math.max(z, 0))).join("x")
    // assemble the uri
    const uri = [reader.api, viewport, dataset.name, channel.tag, tag].join("/")
    // and return it
    return uri
}


// end of file
