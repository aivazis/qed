// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// a relay store updater shared by the mutations that swap a whole view -- {viewReaderSelect} and
// {viewCoordinateToggle} -- and by the {window.qed} automation facade that reuses them. selecting a
// reader or a coordinate replaces the view record wholesale, so relay cannot auto-merge it by id;
// this splices the view the server returned into {QED.views} at {viewport}
export const replaceViewUpdater = (rootField, viewport) => store => {
    // the view the mutation returned
    const view = store.getRootField(rootField)?.getLinkedRecord("view")
    // if the server declined, leave the store alone
    if (view == null) {
        return
    }
    // splice it into the remote store's view list at {viewport}
    const qed = store.get("QED")
    const views = qed.getLinkedRecords("views")
    qed.setLinkedRecords(views.toSpliced(viewport, 1, view), "views")
}


// end of file
