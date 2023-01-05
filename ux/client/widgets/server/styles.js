// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// get colors
import { theme } from '~/palette'


// server info styling
const server = (client, status) => ({
    // the container
    box: {
        // my opinions
        cursor: "default",
        // plus whatever the client said for the container
        ...client?.box,
        // and the text
        ...client?.text,
        // with status specific overrides
        ...client.status?.[status],
    },

    // links
    link: {
        margin: "0.0em 0.5em",
        // with status specific overrides
        ...client.status?.[status],
    },
})


// publish
export default {
    server,
}

// end of file
