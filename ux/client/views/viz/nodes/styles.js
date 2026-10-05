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
const normal = theme.page.normal
const value = theme.page.bright
// the color of the factory names, as the diagram paints them
const factory = "hsl(28deg, 70%, 55%)"


// publish
export default {
    header,
    dim,
    normal,
    value,
    factory,
}


// end of file
