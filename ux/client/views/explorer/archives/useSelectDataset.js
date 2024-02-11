// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2024 all rights reserved


// local
// hooks
import { useArchive } from './useArchive'
import { useViews } from '../explorer/useViews'
import { useGetActiveView } from '../explorer/useGetActiveView'
import { useSetActiveView } from '../explorer/useSetActiveView'
import { useSetActiveViewport } from '../explorer/useSetActiveViewport'


// place {reader} in the active view
export const useSelectDataset = ({ name, uri }) => {
    // get my archive
    const archive = useArchive()
    // get the views
    const { views, emptyView } = useViews()
    // unpack the active view
    const { reader } = useGetActiveView()
    // get the view activator
    const activateView = useSetActiveView()
    // get the viewport activator
    const activateViewport = useSetActiveViewport()

    // deduce my state
    const state = reader?.uri === uri
    // if i'm selected
    if (state) {
        // we are done
        return {
            // when selected
            state: "selected",
            // disable the selector
            selector: () => null
        }
    }

    // otherwise, build the selector
    const selector = () => {
        // look through the views; perhaps i'm already in there
        const already = views.findIndex(view => view.reader?.uri == uri)
        // if i'm there
        if (already > -1) {
            // just activate that viewport
            activateViewport(already)()
            // and done
            return
        }
        // otherwise, check whether i should replace a blank view
        const replace = views.findIndex(view => view.archive === null && view.reader == null)
        // use this to figure where to place my view
        const spot = replace == -1 ? views.length : replace
        // put me in the pile of views
        activateView({
            // start with a clean slate
            ...emptyView(),
            // add the reader description
            reader: {
                name,
                uri,
                archive: archive.uri,
                readers: archive.readers,
            }
        }, spot)
        // and activate that viewport
        activateViewport(spot)()
        // all done
        return
    }
    // all done
    return {
        // the selector
        selector,
        // and my current state
        state: "enabled",
    }
}


// end of file
