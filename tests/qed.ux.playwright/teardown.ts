// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// support
import fs from "fs"


// remove the scratch area the servers under test worked out of
//
// the config points every server at a workspace under a scratch directory of its own making,
// so whatever they derive -- the pyramids of the datasets the specs select -- lands there rather
// than beside the fixtures. playwright runs this after the servers are down, in the process that
// loaded the config, so the location is still in the environment
const teardown = async () => {
    // where the servers worked
    const scratch = process.env.QED_SCRATCH
    // a run that never made one has nothing to remove
    if (!scratch) {
        // so leave
        return
    }
    // otherwise, remove it and everything in it
    fs.rmSync(scratch, { recursive: true, force: true })
    // all done
    return
}

// publish
export default teardown

// end of file
