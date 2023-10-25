// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2023 all rights reserved


// local
// hooks
import { useViews } from "../explorer/useViews"
import { useSetActiveView } from "../explorer/useSetActiveView"
import { useSetActiveViewport } from "../explorer/useSetActiveViewport"


// add the form that collects the new archive form to the set of views
export const useConnectArchive = () => {
    // get the active view
    const { views, activeViewport, emptyView } = useViews()
    // the view activator
    const activateView = useSetActiveView()
    // and the active viewport selector
    const selectActiveViewport = useSetActiveViewport()

    // check whether the new archive form is supposed to replace the current view
    const replace = (
        views.length == 1 &&
        views.archive == null &&
        views.dataset == null &&
        views.newArchive == null &&
        views.newDataset == null
    )
    // either replace or go to the end of the pile
    const targetViewport = replace ? activeViewport : views.length
    // build the viewport activator
    const activateViewport = selectActiveViewport(targetViewport)
    // generate a default value for the new archive info
    const newArchive = {
        // its uri
        uri: null,
    }
    // and create the activator for the new archive form
    const activator = () => {
        // adjust the view
        activateView({ ...emptyView(), newArchive }, targetViewport)
        // activate the view
        activateViewport()
        // all done
        return
    }

    // return the activator
    return activator
}


// end of file
