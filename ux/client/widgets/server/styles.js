// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2022 all rights reserved


// get colors
import { theme } from '~/palette'


// server info styling
const server = (client, status) => ({
    // whatever the client said
    ...client?.box,
    ...client?.text,
    // with status specific overrides
    ...client.status?.[status],
})


// publish
export default {
    server,
}

// end of file
