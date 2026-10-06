// -*- web -*-
// -*- coding: utf-8 -*-
//
// michael a.g. aïvázis <michael.aivazis@para-sim.com>
// (c) 1998-2026 all rights reserved


// looking straight down at the floor: points land where they are, heights are invisible, and
// nothing is in front of anything else
export const flat = {
    // my name, and the key that tells my settings apart
    name: "flat",
    key: "flat",
    // where a point lands
    project: ({ x, y }) => ({ x, y }),
    // the displacement on the floor that moves a point by {dx, dy} on the screen
    ground: ({ dx, dy }) => ({ dx, dy }),
    // the change of height that moves a point by {dy} on the screen
    lift: () => 0,
    // how far up a label of the given category floats
    labelLift: () => 0,
}


// end of file
