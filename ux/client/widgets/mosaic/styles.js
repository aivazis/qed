// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { wheel, theme } from '~/palette'


// publish
export default {
    // the tile container
    mosaic: {
        // this must be sized by the client based on the raster shape
        overflow: "hidden",   // hide anything that sticks out
        // let flex position my children
        display: "flex",
        // the current implementation is just a list of tiles that get wrapped based on their size
        flexDirection: "row",
        flexWrap: "wrap",
    },

    // individual tiles
    tile: {},
}


// end of file
