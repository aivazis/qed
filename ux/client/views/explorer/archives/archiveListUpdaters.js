// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// the store updaters the archive mutations share: relay cannot auto-merge a change to the list
// of connected archives, so the ui hooks and the automation facade shape the store the same way


// the updater for a mutation whose payload carries the archive that was connected under {field}
export const connectArchiveUpdater = field => store => {
    // get the root field of the query result
    const payload = store.getRootField(field)
    // if it's trivial
    if (!payload) {
        // raise an issue
        throw new Error("could not connect to the data archive")
    }
    // ask for the new archive
    const archive = payload.getLinkedRecord("archive")
    // get the session manager
    const qed = store.get("QED")
    // get its connected archives
    const archives = qed.getLinkedRecords("archives")
    // add the new one to the pile
    qed.setLinkedRecords([...archives, archive], "archives")
    // all done
    return
}


// the updater for the mutation that disconnects an archive
export const disconnectArchiveUpdater = store => {
    // get the root field of the query result
    const payload = store.getRootField("disconnectArchive")
    // ask for the target archive
    const archive = payload.getLinkedRecord("archive")
    // if we didn't get back a valid archive
    if (archive === null) {
        // something went wrong at the server; there isn't much more to do
        return
    }
    // get the session manager
    const qed = store.get("QED")
    // get its connected archives
    const archives = qed.getLinkedRecords("archives")
    // remove our target from the pile
    const filtered = archives.filter(
        // by filtering out entries that match its id
        entry => entry.getDataID() !== archive.getDataID()
    )
    // attach the modified pile to the session manager
    qed.setLinkedRecords(filtered, "archives")
    // all done
    return
}


// the updater for a mutation whose payload, under {field}, carries the archive that was at the
// location {previous}; the id of an archive is made from its location, and an archive that was
// renamed is a new one, so the archive comes back as a new record that takes the place of the old
export const reconfigureArchiveUpdater = (previous, field = "reconfigureArchive") => store => {
    // get the root field of the query result
    const payload = store.getRootField(field)
    // ask for the reconfigured archive
    const archive = payload?.getLinkedRecord("archive")
    // if the server could not reconfigure it
    if (!archive) {
        // raise an issue
        throw new Error("could not reconfigure the data archive")
    }
    // get the session manager
    const qed = store.get("QED")
    // get its connected archives
    const archives = qed.getLinkedRecords("archives")
    // put the reconfigured archive in the place of the old one
    const replaced = archives.map(
        // by swapping out the entry at the old location
        entry => entry.getValue("uri") === previous ? archive : entry
    )
    // attach the modified pile to the session manager
    qed.setLinkedRecords(replaced, "archives")
    // all done
    return
}


// end of file
