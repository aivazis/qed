// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// load the page again, against whoever is serving it now
//
// everything a page holds describes the server it was loaded from, so when that server is
// gone for good, or the page has lost track of it, the way back is to start from scratch
//
// the one page that must not do this is the one that stops the server: asking for it again
// repeats the request, so a tab left behind after a shutdown would kill the next server the
// moment it came up. the user of that page was told to close the window, and that stands
//
// this is plain dom, with no react in it
export const startOver = () => {
    // if this is the page that stops the server
    if (/\/stop\/?$/.test(window.location.pathname)) {
        // leave it alone
        return
    }
    // otherwise, go again
    window.location.reload()
    // all done
    return
}


// end of file
