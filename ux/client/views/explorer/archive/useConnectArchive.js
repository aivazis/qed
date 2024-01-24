// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// local
// hooks
import { useViews } from "../explorer/useViews"
import { useSetActiveView } from "../explorer/useSetActiveView"
import { useSetActiveViewport } from "../explorer/useSetActiveViewport"


// add the form that connects the new archive form to the set of views
export const useConnectArchive = () => {
    // get the views
    const { views, emptyView } = useViews()
    // the view activator
    const activateView = useSetActiveView()
    // get the viewport activator
    const activateViewport = useSetActiveViewport()

    // build the view activator
    const activator = () => {
        // look through the views; perhaps there is a blank one to replace
        const already = views.findIndex(view => view.archive == null && view.reader == null)
        // compute my spot
        const spot = already == -1 ? views.length : already
        // place me in the pile of views
        activateView({
            // starting with a clean slate
            ...emptyView(),
            // add an empty archive spec
            archive: {
                uri: null,
            }
        }, spot)
        // activate my target viewport
        activateViewport(spot)()
        // all done
        return
    }
    // return the activator
    return activator
}


// end of file
