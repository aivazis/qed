// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


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
        // look through the views; perhaps i'm already on display
        const already = views.findIndex(view => view.reader?.uri == uri)
        // if i'm there
        if (already > -1) {
            // just activate that viewport, rather than opening a second copy of me
            activateViewport(already)()
            // and done
            return
        }
        // otherwise i take over the viewport the user is looking at. clicking through an
        // archive is browsing, and browsing must not build a pile of views nobody asked
        // for; a viewport comes into being when somebody asks for one, with {split}. the
        // target defaults to the active viewport, so there is nothing to choose here
        activateView({
            // start with a clean slate, so nothing of the previous occupant survives
            ...emptyView(),
            // add the reader description, which the viewport renders as the form that
            // connects me
            reader: {
                name,
                uri,
                archive: archive.uri,
                readers: archive.readers,
            }
        })
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
