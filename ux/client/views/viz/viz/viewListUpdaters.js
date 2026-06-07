// -*- web -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// relay store updaters for the mutations that change the viewport list -- {viewSplit} and
// {viewCollapse} -- shared by their hooks and the {window.qed} automation facade. they reshape the
// {QED.views} list, which relay cannot infer from the mutation result alone

// splice the split-off view in right after {viewport}
export const splitViewUpdater = viewport => store => {
    // the view the server returned
    const view = store.getRootField("viewSplit")?.getLinkedRecord("view")
    // if the server declined, leave the store alone
    if (view == null) {
        return
    }
    // splice it in after the one that split
    const qed = store.get("QED")
    const views = qed.getLinkedRecords("views")
    qed.setLinkedRecords(views.toSpliced(viewport + 1, 0, view), "views")
}

// drop the view at {viewport}, or replace a lone view with the blank one the server returned
export const collapseViewUpdater = viewport => store => {
    // the view the server returned
    const view = store.getRootField("viewCollapse")?.getLinkedRecord("view")
    // if the server declined, leave the store alone
    if (view == null) {
        return
    }
    const qed = store.get("QED")
    const views = qed.getLinkedRecords("views")
    // a lone view collapses to the blank one the server sent back
    if (views.length === 1) {
        qed.setLinkedRecords([view], "views")
        return
    }
    // otherwise drop the one at {viewport}
    qed.setLinkedRecords(views.toSpliced(viewport, 1), "views")
}


// end of file
