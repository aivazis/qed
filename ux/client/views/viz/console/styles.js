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

// the severities, in the order they are shown, and their colors
const severities = ["debug", "info", "warning", "error", "firewall", "help"]

// the color of a severity
const color = severity => theme.journal[severity] ?? theme.page.normal


// publish
export default {
    header,
    severities,
    color,
}

// end of file
