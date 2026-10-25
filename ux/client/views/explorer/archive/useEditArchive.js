// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// local
// hooks
import { useViews } from "../explorer/useViews"
import { useSetActiveView } from "../explorer/useSetActiveView"
import { useSetActiveViewport } from "../explorer/useSetActiveViewport"


// build a function that brings up the form that reconfigures an archive, filled with what the
// archive says about itself
export const useEditArchive = () => {
    // get the current views and the view factory
    const { views, emptyView } = useViews()
    // the view mutator
    const activateView = useSetActiveView()
    // and the viewport selector
    const activateViewport = useSetActiveViewport()

    // the editor
    const editor = archive => {
        // look for an empty view
        const already = views.findIndex(view => view.archive == null && view.reader == null)
        // if there isn't one, add the form at the end
        const spot = already == -1 ? views.length : already
        // put the form in it, with the archive it edits
        activateView({
            // starting from an empty view
            ...emptyView(),
            // the archive part
            archive: {
                // the location the form describes, which starts out as the current one
                uri: archive.uri,
                // and the archive being reconfigured
                edit: archive,
            }
        }, spot)
        // and activate the viewport
        activateViewport(spot)()
        // all done
        return
    }
    // hand it off
    return editor
}


// end of file
