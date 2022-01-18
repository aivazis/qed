// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { theme, wheel } from '~/palette'
// and the base styles
import styles from '../styles'


const viewport = ({ width, height }) => ({
    // the overall box
    box: {
        // layout
        flex: "1 1 100%",
        overflow: "auto",
        minWidth: "300px",
        minHeight: "300px",
        margin: "0.25rem 0.5rem 0.5rem 0.5rem",
        border: "1px solid hsl(28deg, 30%, 15%)",
    },

    // the tile container
    mosaic: {
        backgroundColor: "hsl(0deg, 5%, 7%)",
        width: `${width}px`,
        height: `${height}px`,
    },

    // individual tiles
    tile: {
        backgroundColor: "hsl(28deg, 25%, 7%)",
    },
})

// publish
export default {
    viewport,
}


// end of file
