// -*- web -*-
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


// publish
export default {
    header,
    dim,
    normal,
    danger,
    states,
}


// end of file
