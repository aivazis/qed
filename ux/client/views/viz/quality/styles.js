// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// get colors
import { theme } from '~/palette'
// the base styling for children of the {viz} panel
import styles from '../viz/styles'


// my header
const header = {
    // inherit
    ...styles.activityPanels.header
}

// the colors of text
const dim = theme.page.dim
const normal = theme.page.bright
const danger = theme.page.danger

// the colors of the states of a chunk
const states = theme.quality

// the colors of the pages: the bytes of the raster, of everybody else, and the room left over
const strip = {
    mine: theme.quality.data,
    others: theme.page.dim,
    unused: theme.page.relief,
}

// the colors of the map of the file: the raster in view, as the chunk map draws its data, the other
// rasters of the product, everybody else, the metadata and the free space, and the raster picked
// from the legend
const filemap = {
    mine: theme.quality.data,
    neighbor: theme.quality.neighbor,
    others: theme.quality.others,
    free: theme.page.relief,
    spot: theme.quality.spot,
}

// the color of chunks of fill, by whether the library knows the value they hold
const fill = agrees => agrees === false ? theme.quality.lie : theme.quality.fill

// the outline of the chunks and the page in focus
const focus = theme.page.highlight


// publish
export default {
    header,
    dim,
    normal,
    danger,
    states,
    strip,
    filemap,
    fill,
    focus,
}


// end of file
