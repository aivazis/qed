// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the mount component that publishes {window.qed}
export { Automation } from './Automation'
// the mount component that keeps this client in sync with the server over the event stream
export { LiveSync } from './LiveSync'
// which run of the server this client is talking to
export { instance } from './instance'
// load the page again, against whoever is serving it now
export { startOver } from './startOver'
// whether this client is in touch with its server; the hook that reads it is in {~/hooks}
export { reachability } from './reachability'


// end of file
