// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2021 all rights reserved


// get colors
import { wheel, theme } from '~/palette'
// get the base styles
import base from '~/views/styles'


// publish
export default {
    // the container
    stop: {
        // inherit
        ...base.panel,
    },

    placeholder: {
        position: "fixed",
        top: "50%",
        left: "50%",
        width: "100%",
        textAlign: "center",
        transform: "translate(-50%, -50%)",
    },

}


// end of file
